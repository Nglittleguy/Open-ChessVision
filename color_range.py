import numpy as np
import cv2

#Color is BRG

def color_limits(hue):
  
  # c_dict = {
  #   "red": np.uint8([[[0,0,255]]]),
  #   "blue": np.uint8([[[255, 50, 0]]]),
  #   "green": np.uint8([[[0, 255, 0]]]),
  #   "yellow": np.uint8([[[0, 255, 255]]]),
  #   "purple": np.uint8([[[255, 0, 255]]]),
  # }

  # c = c_dict["red"]

  # if color in c_dict:
  #   c = c_dict[color]

  # hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
  # hue = hsvC[0][0][0]

  # Handle red hue wrap-around
  if hue >= 165:  # Upper limit for divided red hue
      lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
      upperLimit = np.array([180, 255, 255], dtype=np.uint8)
  elif hue <= 15:  # Lower limit for divided red hue
      lowerLimit = np.array([0, 100, 100], dtype=np.uint8)
      upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)
  else:
      lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
      upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)

  return lowerLimit, upperLimit