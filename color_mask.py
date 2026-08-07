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

def color_limits(hue, range):
  # Handle red hue wrap-around
  if hue >= 180-range:  # Upper limit for divided red hue
      lowerLimit = np.array([hue - range, 50, 50], dtype=np.uint8)
      upperLimit = np.array([180, 255, 255], dtype=np.uint8)
  elif hue <= range:  # Lower limit for divided red hue
      lowerLimit = np.array([0, 50, 50], dtype=np.uint8)
      upperLimit = np.array([hue + range, 255, 255], dtype=np.uint8)
  else:
      lowerLimit = np.array([hue - int(range/2), 50, 50], dtype=np.uint8)
      upperLimit = np.array([hue + int(range/2), 255, 255], dtype=np.uint8)

  return lowerLimit, upperLimit

def color_mask(frame, hue, range):
  low, high = color_limits(hue, range)

  frame_blur = cv2.blur(frame, (10,10))
  frame_hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)
  frame_mask = cv2.inRange(frame_hsv, low, high)
  
  return dilate(erode(frame_mask, KERNEL_SIZE), KERNEL_SIZE)