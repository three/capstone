#!/usr/bin/env python2
import time
import picamera
import picamera.array
import numpy as np
import cv2
import math

DOWNSAMPLE_SIZE = 128

print('Setting up camera...')

# Initialize the camera and a stream. The stream will be cleared and reused
# each time
camera = picamera.PiCamera()
stream = picamera.array.PiRGBArray(camera)

# Take a sample picture to get the resolution
camera.capture(stream, format='bgr')
resolution = stream.array.shape[:2]
downsample_scale_x = float(resolution[0]) / DOWNSAMPLE_SIZE
downsample_scale_y = float(resolution[1]) / DOWNSAMPLE_SIZE

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
initmask[:,:] = cv2.GC_PR_FGD
initmask[maskimg == 0] = cv2.GC_FGD
initmask[maskimg == 255] = cv2.GC_BGD

# The foreground and backgroudn models for grabcut.
# These buffers need to bre re-zeroed each time
bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)

# The template image is used to get the position of the razor
trimmer_template = np.zeros((10,10,3), np.uint8)
trimmer_template[:,:,1] = 255

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
    return (
            downsampled_bounds[0] * downsample_scale_x,
            downsampled_bounds[1] * downsample_scale_y,
            downsampled_bounds[2] * downsample_scale_x,
            downsampled_bounds[3] * downsample_scale_y,
            )

def getTrimmerPosition(img):
    res = cv2.matchTemplate(img, trimmer_template, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return min_loc

for i in range(100):
    img = capture()
    head = getHeadBox(img)
    trimmer_pos = getTrimmerPosition(img)
    print(str(head) + ' ' + str(trimmer_pos))
    print()
