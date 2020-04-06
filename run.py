#!/usr/bin/env python2
import time
import picamera
import picamera.array
import numpy as np
import cv2
import math
from matplotlib import pyplot as plt

DOWNSAMPLE_SIZE = 256

print('Setting up camera...')

# Initialize the camera and a stream. The stream will be cleared and reused
# each time
camera = picamera.PiCamera()
stream = picamera.array.PiRGBArray(camera)

# Take a sample picture to get the resolution
camera.capture(stream, format='bgr')
resolution = stream.array.shape[:2]
downsample_scale_x = float(resolution[1]) / DOWNSAMPLE_SIZE
downsample_scale_y = float(resolution[0]) / DOWNSAMPLE_SIZE

print('Camera resolution detected to be ' + str(resolution))
print('downsample_scale_x = ' + str(downsample_scale_x))
print('downsample_scale_y = ' + str(downsample_scale_y))
print()

print("Loading Bullseye and initializing buffers...")

# Load in the bullseye, which forms our starting point for grabcut. Since we downsize before grabcut,
# the downsized image size is used
maskimg = cv2.imread('bullseye.png', 0)
maskimg = cv2.resize(maskimg, (DOWNSAMPLE_SIZE, DOWNSAMPLE_SIZE), interpolation = cv2.INTER_NEAREST)
initmask = np.zeros((DOWNSAMPLE_SIZE, DOWNSAMPLE_SIZE), np.uint8)
initmask[:,:] = cv2.GC_PR_BGD # 1<=x<128
initmask[maskimg > 127] = cv2.GC_PR_FGD # 128<=x<255
initmask[maskimg == 0] = cv2.GC_BGD # x=0
initmask[maskimg == 255] = cv2.GC_FGD # x=255

# The foreground and backgroudn models for grabcut.
# These buffers need to bre re-zeroed each time
bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)

# The template image is used to get the position of the razor
trimmer_template = np.zeros((10,10,3), np.uint8)
trimmer_template[:,:,1] = 255

# Setup the preview window
cv2.startWindowThread()
cv2.namedWindow('Preview')
cv2.imshow('Preview', np.zeros(resolution))

print('Initialization Step Done.')
print()

def capture():
    stream.truncate()
    stream.seek(0)
    camera.capture(stream, format='bgr')
    return stream.array

def getHeadBox(img):
    bgdModel.fill(0)
    bgdModel.fill(0)
    downsampled =  cv2.resize(img, (DOWNSAMPLE_SIZE, DOWNSAMPLE_SIZE), interpolation = cv2.INTER_NEAREST)
    mask = cv2.grabCut(downsampled, initmask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)[0]
    downsampled_bounds = cv2.boundingRect(mask[:,:,np.newaxis])

    #cv2.imshow('Preview', downsampled*mask[:,:,np.newaxis])

    return (
            int(downsampled_bounds[0] * downsample_scale_x),
            int(downsampled_bounds[1] * downsample_scale_y),
            int(downsampled_bounds[2] * downsample_scale_x),
            int(downsampled_bounds[3] * downsample_scale_y),
            )

def getTrimmerPosition(img):
    res = cv2.matchTemplate(img, trimmer_template, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return min_loc

lasttime = time.time()
while True:
    img = capture()
    head = getHeadBox(img)
    trimmer_pos = getTrimmerPosition(img)

    cv2.rectangle(img, head[:2], (head[0]+head[2], head[1]+head[3]), 255, 2)
    cv2.rectangle(img, (0,trimmer_pos[1]), (resolution[1],trimmer_pos[1]), (0,0,255), 1)
    cv2.rectangle(img, (trimmer_pos[0],0), (trimmer_pos[0],resolution[0]), (0,0,255), 1)
    cv2.circle(img, trimmer_pos, 1, (0,0,255), 10)

    cv2.imshow('Preview', img)

    now = time.time()
    elapsed = now - lasttime
    lasttime = now
    print('Time Elapsed: ' + str(elapsed) + 's (' + str(1/elapsed) + 'HZ)')

    in_bounds_x = trimmer_pos[0] >= head[0] and trimmer_pos[0] < head[0]+head[2]
    in_bounds_y = trimmer_pos[1] >= head[1] and trimmer_pos[1] < head[1]+head[3]
    if (not in_bounds_x) or (not in_bounds_y):
        print('Trimmer not on head')
    else:
        percent = 100 - 100 * float(trimmer_pos[1] - head[1]) / head[3]
        print('Trimmer is '+ str(percent) + ' up the head')
