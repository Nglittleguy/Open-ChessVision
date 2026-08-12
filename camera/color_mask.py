import numpy as np
import cv2

#Color is BRG
KERNEL_SIZE = 3

def erode(frame, size):
  kernel = np.ones((size, size), np.uint8)
  frame_eroded = cv2.erode(frame, kernel, iterations=1)
  return frame_eroded

def dilate(frame, size):
  kernel = np.ones((size, size), np.uint8)
  frame_dilated = cv2.dilate(frame, kernel, iterations=1)
  return frame_dilated

# def color_limits(hue, range):
#   # Handle red hue wrap-around
#   if hue >= 180-int(range/2): 
#       lowerLimit = np.array([hue - range, 50, 50], dtype=np.uint8)
#       upperLimit = np.array([180, 255, 255], dtype=np.uint8)
#   elif hue <= int(range/2):  
#       lowerLimit = np.array([0, 50, 50], dtype=np.uint8)
#       upperLimit = np.array([hue + range, 255, 255], dtype=np.uint8)
#   else:
#       lowerLimit = np.array([hue - int(range/2), 50, 50], dtype=np.uint8)
#       upperLimit = np.array([hue + int(range/2), 255, 255], dtype=np.uint8)

#   return lowerLimit, upperLimit

def color_mask(frame, hue, range):

  frame_blur = cv2.blur(frame, (10,10))
  frame_hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)

  # ex. Hue = 175 and Range = 10, should have 165 - 180, and 0 - 5 | 
  # ex. Hue = 4 and Range = 10, should have 4 - 14, and 174 - 180
  if hue >= 180-range:
    low_remaining = hue - (180 - range)
    low_upper_limit = np.array([low_remaining, 255, 255], dtype=np.uint8)
    low_lower_limit = np.array([0, 50, 80], dtype=np.uint8)

    high_upper_limit = np.array([180, 255, 255], dtype=np.uint8)
    high_lower_limit = np.array([hue - range, 50, 100], dtype=np.uint8)

    frame_mask_1 = cv2.inRange(frame_hsv, low_lower_limit, low_upper_limit)
    frame_mask_2 = cv2.inRange(frame_hsv, high_lower_limit, high_upper_limit)
    frame_mask = cv2.bitwise_or(frame_mask_1, frame_mask_2)
  elif hue <= range:
    low_upper_limit = np.array([hue + range, 255, 255], dtype=np.uint8)
    low_lower_limit = np.array([0, 50, 80], dtype=np.uint8)

    high_remaining = 180 - (range - hue)
    high_upper_limit = np.array([180, 255, 255], dtype=np.uint8)
    high_lower_limit = np.array([high_remaining, 50, 80], dtype=np.uint8)

    frame_mask_1 = cv2.inRange(frame_hsv, low_lower_limit, low_upper_limit)
    frame_mask_2 = cv2.inRange(frame_hsv, high_lower_limit, high_upper_limit)
    frame_mask = cv2.bitwise_or(frame_mask_1, frame_mask_2)
    
  else:
    lower_limit = np.array([hue - range, 50, 80], dtype=np.uint8)
    higher_limit = np.array([hue + range, 255, 255], dtype=np.uint8)
    frame_mask = cv2.inRange(frame_hsv, lower_limit, higher_limit)

  return dilate(erode(frame_mask, KERNEL_SIZE), KERNEL_SIZE)

def hue2brg(hue):
  hsv_selected = np.uint8([[[hue, 255, 255]]])
  bgr_selected = cv2.cvtColor(hsv_selected, cv2.COLOR_HSV2BGR)[0][0]
  return (int(bgr_selected[0]), int(bgr_selected[1]), int(bgr_selected[2]))

def brg2hue(brg):
  brg_selected = np.uint8([[brg]])
  hsv_selected = cv2.cvtColor(brg_selected, cv2.COLOR_BRG2HSV)[0][0]
  return hsv_selected[0]