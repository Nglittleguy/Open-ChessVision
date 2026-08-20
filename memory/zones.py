"""
Memory for Zone Selection - 
Choosing areas of interest for the Video Capture to crop
"""

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

def zone_event(event, x, y, flag, params):
  global zones, zone_stage
  zones[zone_stage]["xy"] = (x,y)