import cv2
import memory.zones as z
import memory.selection as m 
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
    cv2.setMouseCallback('Zones', z.zone_event)
    success, zone_frame = vc.read()
    for stage in range(z.zone_stage + 1):
      if stage % 2 == 1 and z.zones[stage]["xy"] != (0,0):
        cv2.rectangle(zone_frame, z.zones[stage-1]["xy"], z.zones[stage]["xy"], (255, 0, 0), m.SELECTION_THICKNESS) 
      cv2.putText(zone_frame, z.zones[stage]["name"], (z.zones[stage]["xy"][0]-40, z.zones[stage]["xy"][1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)

    cv2.imshow("Zones", zone_frame)

    key = cv2.waitKey(10) & 0xFF

    if key == ord(' '): # next on spacebar
      z.zone_stage = z.zone_stage + 1
      if z.zone_stage >= len(z.zones):
        break
  cv2.destroyAllWindows()

  callibration_x_list = [z.zones[0]['xy'][0], z.zones[1]['xy'][0]]
  callibration_y_list = [z.zones[0]['xy'][1], z.zones[1]['xy'][1]]
  board_x_list = [z.zones[2]['xy'][0], z.zones[3]['xy'][0]]
  board_y_list = [z.zones[2]['xy'][1], z.zones[3]['xy'][1]]

  z.zones[0]['xy'] = (min(callibration_x_list), min(callibration_y_list))
  z.zones[1]['xy'] = (max(callibration_x_list), max(callibration_y_list))
  z.zones[2]['xy'] = (min(board_x_list), min(board_y_list))
  z.zones[3]['xy'] = (max(board_x_list), max(board_y_list))
  return


# Step 2: Selecting Callibration for Pieces
def step_2(vc):
  
  success = True
  cv2.namedWindow("Adjustments")

  while success and m.selection_stage < len(m.selection):
    # cv2.setMouseCallback('Board', color_event)
    cv2.setMouseCallback('Samples', m.sample_event)
    # update_sample = False

    success, frame = vc.read()
    sample_frame = frame[z.zones[0]['xy'][1]:z.zones[1]['xy'][1], z.zones[0]['xy'][0]:z.zones[1]['xy'][0]]
    board_frame = frame[z.zones[2]['xy'][1]:z.zones[3]['xy'][1], z.zones[2]['xy'][0]:z.zones[3]['xy'][0]]

    # Update when stage changes
    if m.selection_stage > m.last_stage or m.last_stage > m.selection_stage:
      m.last_stage = m.selection_stage

      # When retrieving selection for pieces
      if m.selection_stage > 0 and m.selection_stage < 8:
        cv2.createTrackbar('Range', 'Adjustments', m.selection[m.selection_stage]['range'], 50, m.nothing)
        cv2.createTrackbar('Brightness', 'Adjustments', m.selection[m.selection_stage]['brightness'], 255, m.nothing)
        cv2.createTrackbar('Saturation', 'Adjustments', m.selection[m.selection_stage]['saturation'], 255, m.nothing)
        cv2.createTrackbar('Y-Offset', 'Adjustments', m.selection[m.selection_stage]['offset'], 150, m.nothing)

    # Need to callibrate (White Balance, and Board Isolation)
    if m.selection_stage > 0: # Stages 1-7
      s = m.selection[m.selection_stage]
      sample_frame, board_frame, _update_sample = m.callibrate_frame(sample_frame, board_frame)
      
      # Retrieve hue of sample
      if s["x"] != 0 and s["y"] != 0:
        s["hue"] = calc_hue(sample_frame, s["x"], s["y"])

      s["range"] = cv2.getTrackbarPos('Range', "Adjustments")
      s["offset"] = cv2.getTrackbarPos('Y-Offset', "Adjustments")
      s["saturation"] = cv2.getTrackbarPos('Saturation', "Adjustments")
      s["brightness"] = cv2.getTrackbarPos('Brightness', "Adjustments")

      # Retrieve colour mask using parameters for this Stage
      
      mask_frame = color_mask(board_frame, s["hue"], s["range"], s["brightness"], s["saturation"])
      s["centers"] = track(mask_frame)
      cv2.imshow("Mask", mask_frame)

    m.draw_hue_picker(sample_frame)

    cv2.imshow("Samples", sample_frame)
    cv2.imshow("Board", board_frame)

    # Only update 0.1s
    key = cv2.waitKey(100) & 0xFF

    if key == ord(' '): # next on spacebar
      m.selection_stage = m.selection_stage + 1
    if key == ord('b'): # b for back
      if m.selection_stage != 0:
        m.selection_stage = m.selection_stage - 1
    if key == ord('<'): # < for rotate CCW
      board_rotation = (board_rotation + 3) % 4
    if key == ord('>'): # > for rotate CCW
      board_rotation = (board_rotation + 1) % 4

  # Clear un-needed windows
  cv2.destroyWindow("Mask")
  cv2.destroyWindow("Blur")
  cv2.destroyWindow("Adjustments")
  return

# Step 3: Waiting for Proper Piece Placement
def step_3(vc):
  success = True

  while success:
    success, frame = vc.read()
    update_sample = False

    success, frame = vc.read()
    sample_frame = frame[z.zones[0]['xy'][1]:z.zones[1]['xy'][1], z.zones[0]['xy'][0]:z.zones[1]['xy'][0]]
    board_frame = frame[z.zones[2]['xy'][1]:z.zones[3]['xy'][1], z.zones[2]['xy'][0]:z.zones[3]['xy'][0]]

    # Maintain callibration, updating periodically
    sample_frame, board_frame, update_sample = m.callibrate_frame(sample_frame, board_frame)
    board_frame_clear = board_frame.copy()

    m.draw_hue_picker(sample_frame)

    for s in range(1,8):
      # Periodically update sample hue
      if update_sample:
        m.selection[m.selection_stage]["hue"] = calc_hue(sample_frame, m.selection[m.selection_stage]["x"], m.selection[m.selection_stage]["y"])

      # If getting board corners
      board_frame_to_mask = board_frame if s == i else board_frame_clear
      mask_frame = color_mask(board_frame_to_mask, m.selection[s]["hue"], m.selection[s]["range"], m.selection[s]['brightness'], m.selection[s]['saturation'])
      m.selection[s]["centers"] = track(mask_frame)

      # Piece Type
      if s > 1:
        m.selection[s]["pieces"], keep_backup = track_piece_side(board_frame_clear, m.selection[s]["centers"], m.selection[s]["backup"], m.selection[s]["hue"], board_frame)

        # If nothing has changed, prevent jittering
        if not keep_backup:
          m.selection[s]["backup"] = m.selection[s]["centers"]

        # Place pieces on the board
        m.put_selection_on_board(board_frame, s)

    # Wait to check required placement before beginning
    if m.wait_for_placement(board_frame):
      break;
    
    cv2.imshow("Samples", sample_frame)
    cv2.imshow("Board", board_frame)

      
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