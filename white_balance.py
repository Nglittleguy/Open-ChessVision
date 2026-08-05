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

    for x in range(2*(selection_size-thickness)):
        for y in range(2*(selection_size-thickness)):
            colors = cc_roi[x, y]
            colors_avg = list(map(lambda a: float(a)/(selection_size-thickness)/(selection_size-thickness), colors))
            wb_r = wb_r + colors_avg[0]
            wb_g = wb_g + colors_avg[1]
            wb_b = wb_b + colors_avg[2]

    wb_min = min(wb_r, wb_g, wb_b)
    wb_offset = (wb_r - wb_min, wb_g - wb_min, wb_b - wb_min)

    print(f"Average: {wb_offset}")
    return wb_offset