import cv2
from color_range import color_limits
from white_balance import calc_white_balance
from PIL import Image
import numpy as np
import pandas
import time

def nothing(x):
    return()

wb_x = 0
wb_y = 0
wb = (0,0,0)
mouse_click = False

def mouse_event(event, x, y, flags, params):
    global wb_y, wb_x, mouse_click
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_click = True
    if not mouse_click:
        wb_x = x
        wb_y = y
    

cv2.namedWindow("raw")
vc = cv2.VideoCapture(0)
vc.set(cv2.CAP_PROP_BUFFERSIZE, 1)
last_time = time.time()

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

'''
Step 1: Get White balance
'''
while rval:
    rval, frame = vc.read()
    

    cv2.setMouseCallback('raw', mouse_event)

    key = cv2.waitKey(10) & 0xFF

    if key == 27 or key == ord('q') or key == ord(' '): # exit on ESC
        break

    cv2.rectangle(frame, (wb_x-30, wb_y-30), (wb_x+30, wb_y+30), (0, 255, 0), 5)  
    cv2.imshow("raw", frame)


    # hueValue = cv2.getTrackbarPos("Hue", "Hue Select Window")
    # hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # lowLimit, highLimit = color_limits(hueValue)
    # mask = cv2.inRange(hsvImage, lowLimit, highLimit)
    # cv2.imshow("mask", mask)
    # mask_ = Image.fromarray(mask)
    # # bbox = mask_.getbbox()

    # # if bbox is not None:
    # #     x1, y1, x2, y2 = bbox

    # #     box_frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

    # # cv2.imshow('frame', box_frame)


cv2.destroyAllWindows()

'''
Step 2: White Balanced Loop
'''

# cv2.namedWindow("mask")
# cv2.namedWindow("Hue Select Window")
# cv2.createTrackbar("Hue", "Hue Select Window", 0, 180, nothing);

while rval:
    rval, frame2 = vc.read()
    frame2_sm = cv2.resize(frame2, (960, 540))
    

    curr_time = time.time()
    print(curr_time - last_time)
    if curr_time - last_time > 5:
        last_time = curr_time
        wb = calc_white_balance(frame2, wb_x, wb_y)
        assert len(wb) == 3
        
    wb_frame = cv2.subtract(frame2_sm, wb)
    cv2.imshow("White Balanced", wb_frame)
    cv2.imshow("Non Balanced", frame2_sm)

    key = cv2.waitKey(10) & 0xFF

    if key == 27 or key == ord('q') or key == ord(' '): # exit on ESC
        break
    
    
cv2.waitKey(0)
cv2.destroyAllWindows()




vc.release()