import cv2
from color_range import color_limits
from white_balance import calc_white_balance
from PIL import Image
import numpy as np
import pandas
import time

SELECTION_SIZE = 15
SELECTION_THICKNESS = 2
FRAME_X = 960
FRAME_Y = 540

def nothing(x):
    return()

wb_xy = [0, 0]
wb = (0,0,0)

def wb_event(_event, x, y, _flags, _params):
    global wb_xy
    wb_xy = [x, y]

selection_stage = 0
'''
0: Board
1: King
2: Queen
3: Bishop
4: Knight
5: Rook
6: Pawn
'''

#            Board,  King, Queen, Bisho, Knigh,  Rook,  Pawn
sample_xy = [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0]]
sample_hue = [0,        0,     0,     0,     0,     0,     0 ]


def sample_event(_event, x, y, _flags, _params):
    global sample_xy, selection_stage
    sample_xy[selection_stage] = [x,y]
    

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
    frame_sm = cv2.resize(frame, (FRAME_X, FRAME_Y))
    

    cv2.setMouseCallback('raw', wb_event)

    key = cv2.waitKey(10) & 0xFF

    if key == 27 or key == ord('q') or key == ord(' '): # exit on ESC, q, spacebar
        break

    cv2.rectangle(frame_sm, (wb_xy[0]-SELECTION_SIZE, wb_xy[1]-SELECTION_SIZE), (wb_xy[0]+SELECTION_SIZE, wb_xy[1]+SELECTION_SIZE), (255, 255, 255), SELECTION_THICKNESS)  
    cv2.imshow("raw", frame_sm)


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
Step 2: Set Up Loop
'''

# cv2.namedWindow("mask")
# cv2.namedWindow("Hue Select Window")
# cv2.createTrackbar("Hue", "Hue Select Window", 0, 180, nothing);

while rval:
    rval, frame2 = vc.read()
    frame2_sm = cv2.resize(frame2, (FRAME_X, FRAME_Y))
    

    curr_time = time.time()
    if curr_time - last_time > 10:
        last_time = curr_time
        wb = calc_white_balance(frame2, wb_xy[0], wb_xy[1], SELECTION_SIZE, FRAME_X, FRAME_Y, SELECTION_THICKNESS)
        assert len(wb) == 3
        
    wb_frame = cv2.subtract(frame2_sm, wb)
    cv2.rectangle(wb_frame, (wb_xy[0]-SELECTION_SIZE, wb_xy[1]-SELECTION_SIZE), (wb_xy[0]+SELECTION_SIZE, wb_xy[1]+SELECTION_SIZE), (255, 255, 255), SELECTION_THICKNESS)  


    cv2.setMouseCallback('White Balanced', sample_event)

    for stage in range(selection_stage + 1):
        cv2.rectangle(frame2_sm, (sample_xy[stage][0]-SELECTION_SIZE, sample_xy[stage][1]-SELECTION_SIZE), (sample_xy[stage][0]+SELECTION_SIZE, sample_xy[stage][1]+SELECTION_SIZE), (0, 0, 255), SELECTION_THICKNESS)  

    cv2.imshow("White Balanced", wb_frame)
    key = cv2.waitKey(10) & 0xFF

    if key == ord(' '): # next on spacebar
        break
    
    
cv2.waitKey(0)
cv2.destroyAllWindows()




vc.release()