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

wb = (0,0,0)

selection_stage = 0
'''
0: White
1: Board
2: King
3: Queen
4: Bishop
5: Knight
6: Rook
7: Pawn
'''

selection_stage_name = ["White",          "Board",       "King",    "Queen",     "Bishop",    "Knight",  "Rook",    "Pawn"]
selection_stage_color = [(255, 255, 255), (150, 0, 255), (0,0,255), (0,150,255), (0,255,255), (0,255,0), (255,0,0), (255,0,150)]

#            White, Board,  King, Queen, Bisho, Knigh,  Rook,  Pawn
sample_xy = [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0]]
sample_hue = [   0,     0,     0,     0,     0,     0,     0,     0 ]


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

# cv2.namedWindow("mask")
# cv2.namedWindow("Hue Select Window")
# cv2.createTrackbar("Hue", "Hue Select Window", 0, 180, nothing);


'''
Step 1: Set Up Loop
'''
last_stage = 0

while rval:
    rval, frame = vc.read()
    frame_sm = cv2.resize(frame, (FRAME_X, FRAME_Y))
    print("Start", frame_sm.shape)
    
    curr_time = time.time()

    if selection_stage > last_stage:
        last_stage = selection_stage
    

    # Add white balance if set already
    if selection_stage > 0:

        # Only check every 10s
        if curr_time - last_time > 0.5:
            last_time = curr_time
            wb = calc_white_balance(frame_sm, sample_xy[0][0], sample_xy[0][1], SELECTION_SIZE, FRAME_X, FRAME_Y, SELECTION_THICKNESS)
            assert len(wb) == 3
        
        frame_sm_float = frame_sm.astype(np.float32)
        for i in range(3):
            frame_sm_float[:,:,i] *= wb[i]
        frame_sm = np.clip(frame_sm_float, 0, 255).astype(np.uint8)

        print("After", frame_sm.shape)

    cv2.setMouseCallback('Set Up', sample_event)

    for stage in range(selection_stage + 1):
        cv2.rectangle(frame_sm, (sample_xy[stage][0]-SELECTION_SIZE, sample_xy[stage][1]-SELECTION_SIZE), (sample_xy[stage][0]+SELECTION_SIZE, sample_xy[stage][1]+SELECTION_SIZE), selection_stage_color[stage], SELECTION_THICKNESS)  
        cv2.putText(frame_sm, selection_stage_name[stage], (sample_xy[stage][0]-30, sample_xy[stage][1]-30), cv2.FONT_HERSHEY_SIMPLEX, 1, selection_stage_color[stage], 1)

    cv2.imshow("Set Up", frame_sm)

    key = cv2.waitKey(10) & 0xFF

    if key == ord(' '): # next on spacebar
        selection_stage = selection_stage + 1
        if selection_stage > 7:
            break
    
    
cv2.waitKey(0)
cv2.destroyAllWindows()




vc.release()