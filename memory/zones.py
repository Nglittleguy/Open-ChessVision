"""
Memory for Zone Selection - 
Choosing areas of interest for the Video Capture to crop
"""

def zone_event(event, x, y, flag, params):
  zones[zone_stage]["xy"] = (x,y)

zone_stage = 0

zones = [
  {
    "name": "Callibration 1",
    "xy": (0,0)
  },
  {
    "name": "Callibration 2",
    "xy": (0,0)
  },
  {
    "name": "Board 1",
    "xy": (0,0)
  },
  {
    "name": "Board 2",
    "xy": (0,0)
  },
]