import cv2
from memory.zones import zones, zone_stage, zone_event
from memory.selection import wb, board_rotation, selection, selection_stage, last_stage, sample_event, nothing, callibrate_frame, SELECTION_THICKNESS, draw_hue_picker
from camera.color_mask import color_mask, hue2brg
from camera.white_balance import calc_white_balance, add_white_balance
from camera.hue_picker_rad import calc_hue
from camera.tracking import track, straighten_chessboard, track_piece_side, CELL_SIZE, BORDER_SIZE
from chess.pieces.piece import PieceType, Piece, PieceColor
from chess.board.board_start_state import INIT_BOARD_STATE
from chess.board.board_index import xy2tracking, notation2xy, coords2xy
import numpy as np
import time

FRAME_X = 960
FRAME_Y = 540
ALPHA = 0.1


# Step 1: Zone Selection
def step_1(vc): 
  success = True

  while success:
    cv2.setMouseCallback('Zones', zone_event)
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
def step_2(vc):
  success = True

  while success and selection_stage < len(selection):
    # cv2.setMouseCallback('Board', color_event)
    cv2.setMouseCallback('Samples', sample_event)
    update_sample = False

    success, frame = vc.read()
    sample_frame = frame[zones[0]['xy'][1]:zones[1]['xy'][1], zones[0]['xy'][0]:zones[1]['xy'][0]]
    board_frame = frame[zones[2]['xy'][1]:zones[3]['xy'][1], zones[2]['xy'][0]:zones[3]['xy'][0]]

    # Update when stage changes
    if selection_stage > last_stage or last_stage > selection_stage:
      last_stage = selection_stage

      # When retrieving selection for pieces
      if selection_stage > 1 and selection_stage < 8:
        cv2.createTrackbar('Range', 'Adjustments', selection[selection_stage]['range'], 50, nothing)
        cv2.createTrackbar('Brightness', 'Adjustments', selection[selection_stage]['brightness'], 255, nothing)
        cv2.createTrackbar('Saturation', 'Adjustments', selection[selection_stage]['saturation'], 255, nothing)
        cv2.createTrackbar('Y-Offset', 'Adjustments', selection[selection_stage]['offset'], 150, nothing)

    # Need to callibrate (White Balance, and Board Isolation)
    if selection_stage > 0: # Stages 1-7
      sample_frame, board_frame, update_sample = callibrate_frame(sample_frame, board_frame)

      # Retrieve hue of sample
      if update_sample and selection[selection_stage]["x"] != 0 and selection[selection_stage]["y"] != 0:
        selection[selection_stage]["hue"] = calc_hue(sample_frame, selection[selection_stage]["x"], selection[selection_stage]["y"])

      selection[selection_stage]["range"] = cv2.getTrackbarPos('Range', "Adjustments")
      selection[selection_stage]["offset"] = cv2.getTrackbarPos('Y-Offset', "Adjustments")
      selection[selection_stage]["saturation"] = cv2.getTrackbarPos('Saturation', "Adjustments")
      selection[selection_stage]["brightness"] = cv2.getTrackbarPos('Brightness', "Adjustments")

      # Retrieve colour mask using parameters for this Stage
      mask_frame = color_mask(board_frame, selection[selection_stage]["hue"], selection[selection_stage]["range"], selection[selection_stage]["brightness"], selection[selection_stage]["saturation"])
      selection[selection_stage]["centers"] = track(mask_frame)
      cv2.imshow("Mask", mask_frame)

    draw_hue_picker(sample_frame)

    cv2.imshow("Samples", sample_frame)
    cv2.imshow("Board", board_frame)

    # Only update 0.1s
    key = cv2.waitKey(100) & 0xFF

    if key == ord(' '): # next on spacebar
      selection_stage = selection_stage + 1
    if key == ord('b'): # b for back
      if selection_stage != 0:
        selection_stage = selection_stage - 1
    if key == ord('<'): # < for rotate CCW
      board_rotation = (board_rotation + 3) % 4
    if key == ord('>'): # > for rotate CCW
      board_rotation = (board_rotation + 1) % 4

  return

def main():
  vc = cv2.VideoCapture(0)
  vc.set(cv2.CAP_PROP_BUFFERSIZE, 1)

  if vc.isOpened(): # first frame
    success, _ = vc.read()
  else:
    success = False

  assert(success, "Video Capture failed to start.")

  step_1(vc)
  step_2(vc)
  

if __name__=="__main__":
  main()