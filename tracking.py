import cv2
import numpy as np
import math
from color_mask import hue2brg

TRACKING_HUE_THRESHOLD = 3
TRACKING_PIECE_FRAME = 15
EXTERIOR_THRESHOLD = 100

ROTATION_ORDER = [
  None,
  cv2.ROTATE_90_CLOCKWISE,
  cv2.ROTATE_180,
  cv2.ROTATE_90_COUNTERCLOCKWISE
]

def edges(frame):
  return cv2.Canny(frame, 30, 200)

def contours(frame):
  ct, _hierarchies = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  return ct

def centers(contour_list):
  tracked_list = []
  for c in contour_list:
    M = cv2.moments(c)
    if M['m00'] != 0:
      cx = int(M['m10']/M['m00'])
      cy = int(M['m01']/M['m00'])
      tracked_list.append((cx,cy))
  return tracked_list
      


def track(frame):
  edge = edges(frame)
  contour_list = contours(edge)
  return centers(contour_list)

  
def straighten_chessboard(frame, board_centers, rotation):
  board_corner_1 = board_corner_2 = board_corner_3 = board_corner_4 = (0,0)
  straightened_corners = [(30,30), (30, 430), (430, 430), (430, 30)]

  if len(board_centers) == 4:
    board_corner_1 = min(board_centers, key=(lambda x: math.dist((0,0), x)))
    board_corner_2 = min(board_centers, key=(lambda x: math.dist((0,len(frame[0])), x)))
    board_corner_3 = min(board_centers, key=(lambda x: math.dist((len(frame),len(frame[0])), x))  )
    board_corner_4 = min(board_centers, key=(lambda x: math.dist((len(frame),0), x)))
    
    corners = [board_corner_1, board_corner_2, board_corner_3, board_corner_4]

    transformation = cv2.getPerspectiveTransform(np.float32(corners), np.float32(straightened_corners))
    straightened_frame = cv2.warpPerspective(frame, transformation, (460, 460))

    if rotation:
      straightened_frame = cv2.rotate(straightened_frame, ROTATION_ORDER[rotation % 4])

    return straightened_frame

  else:
    return frame

def piece_exterior(frame, hue):
  # ex. Hue = 175 and threshold = 10, should have 165 - 180, and 0 - 5 | 
  # ex. Hue = 4 and threshold = 10, should have 4 - 14, and 174 - 180
  hi_threshold = 180 - TRACKING_HUE_THRESHOLD
  value_list = []
  for hsv_row in frame:
    for hsv_pixel in hsv_row:
      h, s, v = hsv_pixel
      if not (abs(h - hue) < TRACKING_HUE_THRESHOLD or (hue > hi_threshold and h < hue - hi_threshold) or (hue < TRACKING_HUE_THRESHOLD and h > 180 - (TRACKING_HUE_THRESHOLD - hue))):
        value_list.append(v)

  if len(value_list):
    return np.mean(value_list)
  else: 
    return 255


def split_threshold(val_list):
  if len(val_list) < 2:
    return 0
  
  i = 1
  gap_i = 1
  max_gap = val_list[1] - val_list[0]

  while i < len(val_list):
    if val_list[i] - val_list[i-1] > max_gap:
      max_gap = val_list[i] - val_list[i-1]
      gap_i = i
    i = i + 1

  return int((val_list[gap_i] + val_list[gap_i-1])/2)
  

def track_piece_side(read_frame, centers, hue, draw_frame):
  # exterior_list = []
  piece_info = []

  for c in centers:
    piece_frame = read_frame[c[1]-TRACKING_PIECE_FRAME:c[1]+TRACKING_PIECE_FRAME, c[0]-TRACKING_PIECE_FRAME:c[0]+TRACKING_PIECE_FRAME]
    if len(piece_frame) and len(piece_frame[0]):
      piece_roi = cv2.cvtColor(piece_frame, cv2.COLOR_BGR2HSV)
      piece_ext = piece_exterior(piece_roi, hue)
      piece_info.append({"center": c, "ext": piece_ext})
    # exterior_list.append(piece_ext)

  # list.sort(exterior_list)
  # split = split_threshold(exterior_list)

  for p in piece_info:
    # if p["ext"] > split:
    if p["ext"] > EXTERIOR_THRESHOLD:
      p["white"] = True
    else:
      p["white"] = False
  return piece_info