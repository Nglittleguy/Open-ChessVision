import numpy as np
import cv2

#Frame coming in is BRG numpy.ndarray -> translate to HSV to get H

def calc_hue(frame, x, y, selection_size, frame_x, frame_y, thickness):
    if y > selection_size and x > selection_size and y < frame_y-selection_size and x < frame_x-selection_size:

        hue_roi = frame[y-selection_size-thickness:y+(selection_size-thickness), x-selection_size-thickness:x+(selection_size-thickness)]

        if len(hue_roi) == 0 or len(hue_roi[0]) == 0 or len(hue_roi[0][0]) == 0:
            return 0
        
        hue_roi_hsv = cv2.cvtColor(hue_roi, cv2.COLOR_BGR2HSV)
        h, _s, _v, _ = cv2.mean(hue_roi_hsv)

        return h
    else:
        return 0