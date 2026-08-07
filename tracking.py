import cv2
import numpy as np

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

  
