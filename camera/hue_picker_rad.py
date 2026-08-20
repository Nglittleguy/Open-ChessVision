import numpy as np
from memory.selection import SELECTION_SIZE, SELECTION_THICKNESS
import cv2

RED_THRESHOLD = 10

#Frame coming in is BRG numpy.ndarray -> translate to HSV to get H

def mean_hue(hue_list):
    hue_rad = hue_list * (2.0 * np.pi / 180.0)

    mean_sin = np.mean(np.sin(hue_rad))
    mean_cos = np.mean(np.cos(hue_rad))
    mean_hue_rad = np.arctan2(mean_sin, mean_cos)

    mean_hue = (mean_hue_rad * 180.0 / (2.0 * np.pi)) % 180.0
    return mean_hue


def calc_hue(frame, x, y):
    frame_x = len(frame[0])
    frame_y = len(frame)
    assert len(frame) and len(frame[0])

    if y > SELECTION_SIZE and x > SELECTION_SIZE and y < frame_y-SELECTION_SIZE and x < frame_x-SELECTION_SIZE:

        hue_roi = frame[y-SELECTION_SIZE-SELECTION_THICKNESS:y+(SELECTION_SIZE-SELECTION_THICKNESS), x-SELECTION_SIZE-SELECTION_THICKNESS:x+(SELECTION_SIZE-SELECTION_THICKNESS)]
        if len(hue_roi) == 0 or len(hue_roi[0]) == 0 or len(hue_roi[0][0]) == 0:
            return 0
        
        hue_roi_hsv = cv2.cvtColor(hue_roi, cv2.COLOR_BGR2HSV)
        hues = hue_roi_hsv[:, :, 0]
        
        return mean_hue(hues)
    else:
        return 0