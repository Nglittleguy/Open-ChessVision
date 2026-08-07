import cv2
import numpy as np
import math

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
  cv2.imshow("Edges", edge)
  contour_list = contours(edge)
  return centers(contour_list)

  
def straighten_chessboard(frame, board_centers):
  board_corner_1 = board_corner_2 = board_corner_3 = board_corner_4 = (0,0)
  straightened_corners = [(30,30), (30, 500), (500, 500), (500, 30)]

  if len(board_centers) == 4:
    board_corner_1 = min(board_centers, key=(lambda x: math.dist((0,0), x)))
    board_corner_2 = min(board_centers, key=(lambda x: math.dist((0,len(frame[0])), x)))
    board_corner_3 = min(board_centers, key=(lambda x: math.dist((len(frame),len(frame[0])), x))  )
    board_corner_4 = min(board_centers, key=(lambda x: math.dist((len(frame),0), x)))
    
    corners = [board_corner_1, board_corner_2, board_corner_3, board_corner_4]

    transformation = cv2.getPerspectiveTransform(np.float32(corners), np.float32(straightened_corners))
    return cv2.warpPerspective(frame, transformation, (530, 530))

  else:
    return frame