from chess.pieces.piece_enums import PieceType, PieceColor
from chess.board.board import draw_board
from camera.white_balance import calc_white_balance, add_white_balance
from camera.tracking import straighten_chessboard, BORDER_SIZE
from camera.color_mask import hue2brg
from memory.zones import zones
import time
import cv2
import numpy as np

"""
Memory for Colour Selection - 
Choosing colours for pieces
"""

SELECTION_SIZE = 15
SELECTION_THICKNESS = 2
WB_CHECK_PERIOD = 5 #seconds
SAMPLE_TEXT_OFFSET = 30

wb = (0,0,0)
board_rotation = 0
selection_stage = 0
last_stage = 0
last_time = 0

'''
0: White
1: Board
2: King
3: Queen
4: Bishop
5: Knight
6: Rook
7: Pawn
8: Starting
'''

selection = [
  {
    "name": "White",
    "color": (255, 255, 255),
    "x": 0,
    "y": 0,
    "range": 25,
    "brightness": 100,
    "saturation": 100,
    "hue": 0,
    "centers": [],
    "backup": [],
    "offset": 0,
    "pieces": [],
    "type": PieceType.NULL
  }, 
  {
    "name": "Board",
    "color": (150, 0, 255),
    "x": 0,
    "y": 0,
    "range": 5,
    "brightness": 100,
    "saturation": 100,
    "hue": 0,
    "centers": [],
    "backup": [],
    "offset": 0,
    "pieces": [],
    "type": PieceType.NULL
  }, 
  {
    "name": "King",
    "color": (0, 0, 255),
    "x": 0,
    "y": 0,
    "range": 5,
    "brightness": 90,
    "saturation": 100,
    "hue": 0,
    "centers": [],
    "backup": [],
    "offset": 0,
    "start": 2,
    "pieces": [],
    "type": PieceType.KING
  }, 
  {
    "name": "Queen",
    "color": (0, 150, 255),
    "x": 0,
    "y": 0,
    "range": 3,
    "brightness": 180,
    "saturation": 100,
    "hue": 0,
    "centers": [], 
    "backup": [],
    "offset": 0,
    "start": 2,
    "pieces": [],
    "type": PieceType.QUEEN
  }, 
  {
    "name": "Bishop", 
    "color": (0, 255, 255),
    "x": 0,
    "y": 0,
    "range": 5, 
    "brightness": 50,
    "saturation": 20,
    "hue": 0,
    "centers": [],
    "backup": [],
    "offset": 0,
    "start": 4,
    "pieces": [],
    "type": PieceType.BISHOP
  }, 
  {
    "name": "Knight",
    "color": (0, 255, 0),
    "x": 0,
    "y": 0,
    "range": 30,
    "brightness": 100,
    "saturation": 10,
    "hue": 0,
    "centers": [],
    "backup": [],
    "offset": 0,
    "start": 4,
    "pieces": [],
    "type": PieceType.KNIGHT
  }, 
  {
    "name": "Rook",
    "color": (255, 100, 0),
    "x": 0,
    "y": 0,
    "range": 5,
    "brightness": 65,
    "saturation": 30,
    "hue": 0,
    "centers": [],
    "backup": [],
    "offset": 0,
    "start": 4,
    "pieces": [],
    "type": PieceType.ROOK
  }, 
  {
    "name": "Pawn",
    "color": (255, 0, 150),
    "x": 0,
    "y": 0,
    "range": 15,
    "brightness": 45,
    "saturation": 65,
    "hue": 0,
    "centers": [],
    "backup": [],
    "offset": 0,
    "start": 16,
    "pieces": [],
    "type": PieceType.PAWN
  }
]

def sample_event(_event, x, y, _flags, _params):
  selection[selection_stage]["x"] = x
  selection[selection_stage]["y"] = y

def nothing(x):
  return()

# Add White Balance, and Straighten Board
def callibrate_frame(sample_frame, board_frame):
  global last_time
  curr_time = time.time()
  update = curr_time - last_stage > WB_CHECK_PERIOD

  # Regardless of which direction the box is drawn
  assert len(sample_frame) and len(sample_frame[0])

  # Only check WB periodically
  if update:
    last_time = curr_time
    wb = calc_white_balance(sample_frame, selection[0]["x"], selection[0]["y"], SELECTION_SIZE, SELECTION_THICKNESS)
    assert len(wb) == 3
    return add_white_balance(sample_frame, wb)

  # Update if board corners are found
  if selection_stage > 1:
    board_frame, keep_backup = straighten_chessboard(board_frame, selection[1]["centers"], selection[1]['backup'], board_rotation)
    if not keep_backup:
      selection[1]['backup'] = selection[1]['centers']

  board_frame = add_white_balance(board_frame, wb)

  return sample_frame, board_frame, update


# Draw Hue Picker Squares On Sample Frame
def draw_hue_picker(frame):
  for s in range(selection_stage + 1):
    cv2.rectangle(frame, (selection[s]["x"]-SELECTION_SIZE, selection[s]["y"]-SELECTION_SIZE), (selection[s]["x"]+SELECTION_SIZE, selection[s]["y"]+SELECTION_SIZE), selection[s]["color"], SELECTION_THICKNESS) 
    cv2.putText(frame, selection[s]["name"], (selection[s]["x"]-SAMPLE_TEXT_OFFSET, selection[s]["y"]-SAMPLE_TEXT_OFFSET), cv2.FONT_HERSHEY_SIMPLEX, 1, selection[s]["color"], 1)


# Draw Selection on Board Frame
def draw_selection(frame):
  cv2.putText(frame, "Count: " + str(len(selection[selection_stage]["centers"])), (BORDER_SIZE,BORDER_SIZE), cv2.FONT_HERSHEY_SIMPLEX, 1, hue2brg(selection[selection_stage]["hue"]), 1)

  for c in selection[selection_stage]["centers"]:
    cv2.circle(frame, np.add(c, (0,selection[selection_stage]["offset"])), 7, selection[selection_stage]["color"], 3)
    cv2.circle(frame, np.add(c, (0,selection[selection_stage]["offset"])), 10, (255, 255, 255), 3)

  # Draw board cells if the corners are already found
  if selection_stage > 1:
    draw_board(frame)
  