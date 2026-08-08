import numpy as np
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


def calc_hue(frame, x, y, selection_size, frame_x, frame_y, thickness):
    if y > selection_size and x > selection_size and y < frame_y-selection_size and x < frame_x-selection_size:

        hue_roi = frame[y-selection_size-thickness:y+(selection_size-thickness), x-selection_size-thickness:x+(selection_size-thickness)]
        if len(hue_roi) == 0 or len(hue_roi[0]) == 0 or len(hue_roi[0][0]) == 0:
            return 0
        
        hue_roi_hsv = cv2.cvtColor(hue_roi, cv2.COLOR_BGR2HSV)
        hues = hue_roi_hsv[:, :, 0]
        
        return mean_hue(hues)
    else:
        return 0