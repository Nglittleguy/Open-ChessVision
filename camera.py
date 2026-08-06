import cv2
from color_mask import color_mask
from white_balance import calc_white_balance, add_white_balance
from hue_picker import calc_hue
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
    
vc = cv2.VideoCapture(0)
vc.set(cv2.CAP_PROP_BUFFERSIZE, 1)
last_time = time.time()

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

'''
Step 1: Set Zones
'''
zone_stage = 0
zones = [
    {
        "name": "Callibration 1",
        "xy": (0,0)
    },
    {
        "name": "Callibration 2",
        "xy": (0,0)
    },
    {
        "name": "Board 1",
        "xy": (0,0)
    },
    {
        "name": "Board 2",
        "xy": (0,0)
    },
]

def zone_event(event, x, y, flag, params):
    global zones, zone_stage
    zones[zone_stage]["xy"] = (x,y)

while rval:
    rval, zone_frame = vc.read()
    cv2.setMouseCallback('Zones', zone_event)

    for stage in range(zone_stage + 1):
        if stage % 2 == 1 and zones[stage]["xy"] != (0,0):
            cv2.rectangle(zone_frame, zones[stage-1]["xy"], zones[stage]["xy"], (255, 0, 0), SELECTION_THICKNESS)  
        cv2.putText(zone_frame, zones[stage]["name"], (zones[stage]["xy"][0]-40, zones[stage]["xy"][1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)

    cv2.imshow("Zones", zone_frame)

    key = cv2.waitKey(10) & 0xFF

    if key == ord(' '): # next on spacebar
        zone_stage = zone_stage + 1
        if zone_stage >= len(zones):
            break

cv2.destroyAllWindows()

'''
Step 2: Sample Set Up Loop
'''
cv2.namedWindow("Range Selection")
cv2.createTrackbar('Range', 'Range Selection', 0, 50, nothing)

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

selection = [
    {
        "name": "White",
        "color": (255, 255, 255),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    {
        "name": "Board",
        "color": (150, 0, 255),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    {
        "name": "King",
        "color": (0, 0, 255),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    {
        "name": "Queen",
        "color": (0, 150, 255),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    {
        "name": "Bishop",
        "color": (0, 255, 255),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    {
        "name": "Knight",
        "color": (0, 255, 0),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    {
        "name": "Rook",
        "color": (255, 0, 0),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    {
        "name": "Pawn",
        "color": (255, 0, 150),
        "x": 0,
        "y": 0,
        "range": 25,
        "hue": 0
    }, 
    
]

def sample_event(_event, x, y, _flags, _params):
    global selection, selection_stage
    selection[selection_stage]["x"] = x
    selection[selection_stage]["y"] = y

last_stage = 0

while rval:
    rval, frame = vc.read()
    sample_frame = frame[zones[0]['xy'][1]:zones[1]['xy'][1], zones[0]['xy'][0]:zones[1]['xy'][0]]
    board_frame = frame[zones[2]['xy'][1]:zones[3]['xy'][1], zones[2]['xy'][0]:zones[3]['xy'][0]]
    
    sample_frame_x = int(abs(zones[0]['xy'][0]-zones[1]['xy'][0]))
    sample_frame_y = int(abs(zones[0]['xy'][1]-zones[1]['xy'][1]))
    
    curr_time = time.time()

    if selection_stage > last_stage:
        last_stage = selection_stage

    
    # Add white balance if set already
    if selection_stage > 0:

        # Only check every 5s
        if curr_time - last_time > 5:
            last_time = curr_time
            wb = calc_white_balance(sample_frame, selection[0]["x"], selection[0]["y"], SELECTION_SIZE, sample_frame_x, sample_frame_y, SELECTION_THICKNESS)
            assert len(wb) == 3
        
        selection[selection_stage]["range"] = cv2.getTrackbarPos('Range', 'Range Selection')
        sample_frame = add_white_balance(sample_frame, wb)
        board_frame = add_white_balance(board_frame, wb)

        if selection[selection_stage]["x"] != 0 and selection[selection_stage]["y"] != 0:
            selection[selection_stage]["hue"] = calc_hue(sample_frame, selection[selection_stage]["x"], selection[selection_stage]["y"], SELECTION_SIZE, sample_frame_x, sample_frame_y, SELECTION_THICKNESS)
        
        mask_frame = color_mask(board_frame, selection[selection_stage]["hue"], selection[selection_stage]["range"])

    cv2.setMouseCallback('Samples', sample_event)
    

    for stage in range(selection_stage + 1):
        cv2.rectangle(sample_frame, (selection[stage]["x"]-SELECTION_SIZE, selection[stage]["y"]-SELECTION_SIZE), (selection[stage]["x"]+SELECTION_SIZE, selection[stage]["y"]+SELECTION_SIZE), selection[stage]["color"], SELECTION_THICKNESS)  
        cv2.putText(sample_frame, selection[stage]["name"], (selection[stage]["x"]-30, selection[stage]["y"]-30), cv2.FONT_HERSHEY_SIMPLEX, 1, selection[stage]["color"], 1)
    
    if selection_stage > 0:
        hsv_selected = np.uint8([[[selection[selection_stage]['hue'], 255, 255]]])
        bgr_selected = cv2.cvtColor(hsv_selected, cv2.COLOR_HSV2BGR)[0][0]
        
        cv2.putText(
            board_frame, 
            "Color", 
            (30,30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (int(bgr_selected[0]), int(bgr_selected[1]), int(bgr_selected[2])),
            1)
        cv2.imshow("Mask", mask_frame)
    
    cv2.imshow("Samples", sample_frame)
    cv2.imshow("Board", board_frame)

    key = cv2.waitKey(10) & 0xFF

    if key == ord(' '): # next on spacebar
        selection_stage = selection_stage + 1
        if selection_stage >= len(selection):
            break
    

cv2.destroyAllWindows()




vc.release()