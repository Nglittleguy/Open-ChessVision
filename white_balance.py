import numpy as np
import cv2

#Frame coming in is BRG numpy.ndarray

def calc_white_balance(frame, wb_x, wb_y, selection_size, frame_x, frame_y, thickness):
    assert wb_y > selection_size and wb_x > selection_size and wb_y < frame_y-selection_size and wb_x < frame_x-selection_size, f"ERROR: Outside camera bounds: x:{wb_x}, y:{wb_y}"

    wb_r = 0
    wb_g = 0
    wb_b = 0

    cc_roi = frame[wb_y-selection_size-thickness:wb_y+(selection_size-thickness), wb_x-selection_size-thickness:wb_x+(selection_size-thickness)]
    cv2.imshow("Color Correction (Pre)", cc_roi)

    wb_b, wb_g, wb_r, _ = cv2.mean(cc_roi)
    target_avg = (wb_b + wb_g + wb_r) / 3.0

    gain_b = target_avg / wb_b
    gain_g = target_avg / wb_g
    gain_r = target_avg / wb_r

    wb_offset = (gain_b, gain_g, gain_r)

    print(f"Average: {wb_offset}")
    return wb_offset