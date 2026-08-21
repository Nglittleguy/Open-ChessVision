import cv2
import numpy as np
import math
from camera.color_mask import hue2brg
import memory.selection as m

TRACKING_HUE_THRESHOLD = 15
TRACKING_PIECE_FRAME = 15
EXTERIOR_THRESHOLD = 150

BOARD_SIZE = 400
CELL_SIZE = int(BOARD_SIZE/8)
BORDER_SIZE = 30
DIFF_THRESHOLD = 8

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

  def sort_coords(coord):
    return (coord[0] * coord[0] + coord[1] * coord[1])

  tracked_list.sort(key=sort_coords)

  return tracked_list
      
def track(frame):
  edge = edges(frame)
  contour_list = contours(edge)
  return centers(contour_list)


# Assuming sorted centers
def use_backup_corners(centers, backup):
  if len(backup) != 4:
    return False
  
  similar = 0
  for b in backup:
    if any(math.dist(b, c) for c in centers):
      similar = similar + 1
      
  return len(centers) < 4 or similar >= 3 # if 3 corners match, then should be good to keep

  
# Assuming sorted centers
def use_backup_filter(centers, backup):
  if len(centers) != len(backup) or len(backup) == 0:
    return False

  b_counter = 0 
  for i in range(len(centers)):
    if math.dist(centers[i], backup[b_counter]) < DIFF_THRESHOLD:
      b_counter = b_counter + 1

  return b_counter == len(backup)
  
  
def straighten_chessboard(frame, board_centers, backup, rotation):
  corners = board_centers
  keep_backup = False
  if use_backup_corners(board_centers, backup):
    corners = backup
    keep_backup = True

  board_corner_1 = board_corner_2 = board_corner_3 = board_corner_4 = (0,0)
  straightened_corners = [(BORDER_SIZE,BORDER_SIZE), (BORDER_SIZE, BORDER_SIZE+BOARD_SIZE), (BORDER_SIZE+BOARD_SIZE, BORDER_SIZE+BOARD_SIZE), (BORDER_SIZE+BOARD_SIZE, BORDER_SIZE)]

  if len(corners) == 4:
    board_corner_1 = min(corners, key=(lambda x: math.dist((0,0), x)))
    board_corner_2 = min(corners, key=(lambda x: math.dist((0,len(frame[0])), x)))
    board_corner_3 = min(corners, key=(lambda x: math.dist((len(frame),len(frame[0])), x))  )
    board_corner_4 = min(corners, key=(lambda x: math.dist((len(frame),0), x)))
    
    corners = [board_corner_1, board_corner_2, board_corner_3, board_corner_4]

    transformation = cv2.getPerspectiveTransform(np.float32(corners), np.float32(straightened_corners))
    straightened_frame = cv2.warpPerspective(frame, transformation, (BORDER_SIZE+BOARD_SIZE+BORDER_SIZE, BORDER_SIZE+BOARD_SIZE+BORDER_SIZE))

    if rotation:
      straightened_frame = cv2.rotate(straightened_frame, ROTATION_ORDER[rotation % 4])

    return straightened_frame, keep_backup

  else:
    return frame, keep_backup

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
    val = np.mean(value_list)

    ## find a value in the 66th percentile brightest pixel (avoid hotspots, glare, and shadows)
    # value_list.sort(reverse=True)
    # val = value_list[int(len(value_list)/3)] 
    
    return val 
  else: 
    return 255

# Input is the frame (HSV), and a single coordinate, and the expected hue
def piece_exterior_is_black(hsv_frame, center, hue):
  dir = [(0,1), (1,0), (0,-1), (-1,0)]
  hi_threshold = 180 - TRACKING_HUE_THRESHOLD
  dark_sides = 0

  # Go in 4 directions
  for d in dir:
    for distance in range (TRACKING_PIECE_FRAME):
      if len(hsv_frame) > 0 and center[0] + d[0] * distance >= 0 and center[1] + d[1] * distance >=0 and center[1] + d[0] * distance < len(hsv_frame) and center[0] + d[1] * distance < len(hsv_frame[0]):
        h, s, v = hsv_frame[center[1] + d[0] * distance][center[0] + d[1] * distance] # order needs to flip because X,Y coordinate is Y,X in cv2

        # If they reach another colour, or a dark spot
        if not (abs(h - hue) < TRACKING_HUE_THRESHOLD or (hue > hi_threshold and h < hue - hi_threshold) or (hue < TRACKING_HUE_THRESHOLD and h > 180 - (TRACKING_HUE_THRESHOLD - hue))) or v < m.bw_threshold:
          
          # Only add the side if they are dark enough
          if v < m.bw_threshold:
            dark_sides = dark_sides + 1
          
          break

  # If all 4 directions reach a black border, then this is a black piece 
  return dark_sides == 4

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
  

def track_piece_side(read_frame, centers, backup, hue, draw_frame):
  frame_hsv = cv2.cvtColor(read_frame, cv2.COLOR_BGR2HSV)

  piece_centers = centers
  keep_backup = False
  # if use_backup_filter(centers, backup):
  #   piece_centers = backup
  #   keep_backup = True
    
  piece_info = []

  if len(frame_hsv) and len(frame_hsv[0]):
    for c in piece_centers:
      piece_info.append(
        {
          "white": not piece_exterior_is_black(frame_hsv, c, hue),
          "center": c
        }
      )

  return piece_info, keep_backup