import numpy as np
from memory.selection import SELECTION_SIZE, SELECTION_THICKNESS
import cv2

#Frame coming in is BRG numpy.ndarray -> translate to HSV to get H

def calc_hue(frame, x, y):
    frame_x = len(frame[0])
    frame_y = len(frame)
    assert len(frame) and len(frame[0])

    if y > SELECTION_SIZE and x > SELECTION_SIZE and y < frame_y-SELECTION_SIZE and x < frame_x-SELECTION_SIZE:

        hue_roi = frame[y-SELECTION_SIZE-SELECTION_THICKNESS:y+(SELECTION_SIZE-SELECTION_THICKNESS), x-SELECTION_SIZE-SELECTION_THICKNESS:x+(SELECTION_SIZE-SELECTION_THICKNESS)]

        if len(hue_roi) == 0 or len(hue_roi[0]) == 0 or len(hue_roi[0][0]) == 0:
            return 0
        
        hue_roi_hsv = cv2.cvtColor(hue_roi, cv2.COLOR_BGR2HSV)
        h, _s, _v, _ = cv2.mean(hue_roi_hsv)

        return h
    else:
        return 0