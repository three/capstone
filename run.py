#!/usr/bin/env python3
import time
import numpy as np
import cv2
import math
import argparse
import os

DOWNSAMPLE_SIZE = 256

argparser = argparse.ArgumentParser(
    description='Smart Trimmer Capstone')
argparser.add_argument('source', type=str,
    help='Gets passed into cv2.VideoCapture, converted to int if possible')
argparser.add_argument('--video', dest='video', action='store_true')
argparser.add_argument('--no-video', dest='video', action='store_false')
argparser.set_defaults(video=False)
args = argparser.parse_args()

print('Setting up capture source...')
capture = None
try:
    capture = cv2.VideoCapture(int(args.source))
except ValueError:
    capture = cv2.VideoCapture(args.source)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
print()

if not args.video:
    print('Setting up Preview Window...')
    cv2.startWindowThread()
    cv2.namedWindow('Result')
    cv2.namedWindow('GrabCut')
    cv2.imshow('Result', np.zeros((256,256)))
    cv2.imshow('GrabCut', np.zeros((256,256)))
    print()

print('Taking sample image to get resolution...')
ret, frame =  capture.read()
if not args.video:
    cv2.imshow('Result', frame)
resolution = frame.shape[:2]
print('resolution = ', resolution)
print()

print('Calculating Downsample Scaling...')
downsample_scale_x = float(resolution[1]) / DOWNSAMPLE_SIZE
downsample_scale_y = float(resolution[0]) / DOWNSAMPLE_SIZE
print('downsample_scale_x = ' + str(downsample_scale_x))
print('downsample_scale_y = ' + str(downsample_scale_y))
print()

print('Initializing Bullseye...')
maskimg = cv2.imread('bullseye2.png', 0)
maskimg = cv2.resize(maskimg, (DOWNSAMPLE_SIZE, DOWNSAMPLE_SIZE), interpolation = cv2.INTER_NEAREST)
initmask = np.zeros((DOWNSAMPLE_SIZE, DOWNSAMPLE_SIZE), np.uint8)
initmask[:,:] = cv2.GC_PR_BGD # 1<=x<128
initmask[maskimg > 127] = cv2.GC_PR_BGD # 128<=x<255
initmask[maskimg == 0] = cv2.GC_BGD # x=0
initmask[maskimg == 255] = cv2.GC_FGD # x=255
print()

print('Initializing Buffers for GrabCut...')
# The foreground and backgroudn models for grabcut.
# These buffers need to bre re-zeroed each time
bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)
print()

print('Initializing Trimmer Template...')
trimmer_template = cv2.imread('template.png')
print()

# Setup the preview window

print('Initialization Step Done.')
print()

def getFrame():
    ret, frame = capture.read()
    if ret:
        return frame
    else:
        return None

def getHeadBox(img):
    # The background and foreground models must be zero-ed each time
    bgdModel.fill(0)
    fgdModel.fill(0)

    # Downsample the image so grabcut runs faster
    downsampled =  cv2.resize(img, (DOWNSAMPLE_SIZE, DOWNSAMPLE_SIZE), interpolation = cv2.INTER_NEAREST)

    # Run Grabcut
    mask = cv2.grabCut(downsampled, initmask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)[0]
    mask = np.where((mask == 2)|(mask == 0),0,1).astype('uint8')

    # Get rectangle containing points
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    print('len(contours) = ', len(contours))

    contour = max(contours, key = cv2.contourArea)
    downsampled_bounds = cv2.boundingRect(contour)

    # Show for debug purposes
    print('downsampled_bounds = ', downsampled_bounds)

    if not args.video:
        cv2.imshow('GrabCut', downsampled*mask[:,:,np.newaxis])

    # Adjust back to un-downsized image and return
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
iteration = 0
while True:
    print('Processing Image for frame ' + str(iteration))

    print('Getting Frame...')
    img = getFrame()

    print('Getting Box Around Head...')
    head = getHeadBox(img)
    print('head = ', head)

    print('Getting Trimmer Position...')
    trimmer_pos = getTrimmerPosition(img)
    in_bounds_x = trimmer_pos[0] >= head[0] and trimmer_pos[0] < head[0]+head[2]
    in_bounds_y = trimmer_pos[1] >= head[1] and trimmer_pos[1] < head[1]+head[3]
    percent = None
    if (not in_bounds_x) or (not in_bounds_y):
        print('Trimmer not on head')
    else:
        percent = 100 - 100 * float(trimmer_pos[1] - head[1]) / head[3]
        print('Trimmer is '+ str(percent) + '% up the head')

    print('Drawing annotated image...')
    cv2.rectangle(img, head[:2], (head[0]+head[2], head[1]+head[3]), 255, 2)
    cv2.rectangle(img, (0,trimmer_pos[1]), (resolution[1],trimmer_pos[1]), (0,0,255), 1)
    cv2.rectangle(img, (trimmer_pos[0],0), (trimmer_pos[0],resolution[0]), (0,0,255), 1)
    cv2.circle(img, trimmer_pos, 1, (0,0,255), 10)

    percent_str = 'Trimmer not on head'
    if percent is not None:
        percent_str = 'Position up head: ' + str(round(percent)) + '%'
    cv2.putText(img, percent_str, (30,30), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0))

    if args.video:
        cv2.imwrite(os.getcwd() + '/out/frame' + str(iteration) + '.png', img)
    else:
        cv2.imshow('Result', img)

    now = time.time()
    elapsed = now - lasttime
    lasttime = now
    print('Time Elapsed: ' + str(elapsed) + 's (' + str(1/elapsed) + 'HZ)')


    print('Done.')
    cv2.waitKey()
    print()

    iteration += 1
