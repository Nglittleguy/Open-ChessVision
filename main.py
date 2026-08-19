import cv2
from memory.zones import zones, zone_stage, zone_event
from camera.color_mask import color_mask, hue2brg
from camera.white_balance import calc_white_balance, add_white_balance
from camera.hue_picker_rad import calc_hue
from camera.tracking import track, straighten_chessboard, track_piece_side, CELL_SIZE, BORDER_SIZE
from chess.pieces.piece import PieceType, Piece, PieceColor
from chess.board.board_start_state import INIT_BOARD_STATE
from chess.board.board_index import xy2tracking, notation2xy, coords2xy
import numpy as np
import time

SELECTION_SIZE = 15
SELECTION_THICKNESS = 2
FRAME_X = 960
FRAME_Y = 540
ALPHA = 0.1


# Step 1: Zone Selection
def step_1(vc): 
  if vc.isOpened(): # first frame
    success, _ = vc.read()
  else:
    success = False
  cv2.setMouseCallback('Zones', zone_event)

  while success:
    success, zone_frame = vc.read()
    for stage in range(zone_stage + 1):
      if stage % 2 == 1 and zones[stage]["xy"] != (0,0):
        cv2.rectangle(zone_frame, zones[stage-1]["xy"], zones[stage]["xy"], (255, 0, 0), SELECTION_THICKNESS) 
      cv2.putText(zone_frame, zones[stage]["name"], (zones[stage]["xy"][0]-40, zones[stage]["xy"][1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)

    cv2.imshow("Zones", zone_frame)

    key = cv2.waitKey(10) & 0xFF

    if key == ord(' '): # next on spacebar
      zone_stage = zone_stage + 1
      if zone_stage >= len(zones):
        break
  cv2.destroyAllWindows()

  callibration_x_list = [zones[0]['xy'][0], zones[1]['xy'][0]]
  callibration_y_list = [zones[0]['xy'][1], zones[1]['xy'][1]]
  board_x_list = [zones[2]['xy'][0], zones[3]['xy'][0]]
  board_y_list = [zones[2]['xy'][1], zones[3]['xy'][1]]

  zones[0]['xy'] = (min(callibration_x_list), min(callibration_y_list))
  zones[1]['xy'] = (max(callibration_x_list), max(callibration_y_list))
  zones[2]['xy'] = (min(board_x_list), min(board_y_list))
  zones[3]['xy'] = (max(board_x_list), max(board_y_list))
  return


# Step 2: 

def main():
  vc = cv2.VideoCapture(0)
  vc.set(cv2.CAP_PROP_BUFFERSIZE, 1)
  last_time = time.time()

  step_1(vc)
  

if __name__=="__main__":
  main()