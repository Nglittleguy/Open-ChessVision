import cv2
import numpy as np
import memory.zones as z
import memory.selection as m 
from camera.color_mask import color_mask
from camera.hue_picker_rad import calc_hue
from camera.tracking import track, track_piece_side

import asyncio
import base64
import threading
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from chess.board.board import Board

FRAME_X = 960
FRAME_Y = 540
ALPHA = 0.1
PIECE_ARRAY_SIZE = 8


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
      if m.selection_stage > 0:
        cv2.createTrackbar('Range', 'Adjustments', m.selection[m.selection_stage]['range'], 50, m.nothing)
        cv2.createTrackbar('Brightness', 'Adjustments', m.selection[m.selection_stage]['brightness'], 255, m.nothing)
        cv2.createTrackbar('Saturation', 'Adjustments', m.selection[m.selection_stage]['saturation'], 255, m.nothing)
        cv2.createTrackbar('Y-Offset', 'Adjustments', m.selection[m.selection_stage]['offset'], 150, m.nothing)

    # Need to callibrate (White Balance, and Board Isolation)
    if m.selection_stage > 0: # Stages 1-7
      s = m.selection[m.selection_stage]
      sample_frame, board_frame, _board_frame_wb, _update_sample = m.callibrate_frame(sample_frame, board_frame, 2)
      
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

    sample_frame = m.draw_hue_picker(sample_frame)
    board_frame = m.draw_selection(board_frame)
    combined_frame = board_frame
    
    if m.selection_stage >= 1 and m.selection_stage < PIECE_ARRAY_SIZE:
      board_frame = cv2.resize(board_frame, (460, 460), interpolation=cv2.INTER_AREA)
      mask_frame = cv2.resize(mask_frame, (460, 460), interpolation=cv2.INTER_AREA)
      combined_frame = np.concatenate((board_frame, cv2.cvtColor(mask_frame, cv2.COLOR_GRAY2RGB)), axis=1)

    cv2.imshow("Samples", sample_frame)
    cv2.imshow("Board", combined_frame)

    # Only update 0.1s
    key = cv2.waitKey(100) & 0xFF

    if key == ord(' '): # next on spacebar

      if m.selection_stage > 0 and m.selection_stage < len(m.selection):
        s["range"] = cv2.getTrackbarPos('Range', "Adjustments")
        s["offset"] = cv2.getTrackbarPos('Y-Offset', "Adjustments")
        s["saturation"] = cv2.getTrackbarPos('Saturation', "Adjustments")
        s["brightness"] = cv2.getTrackbarPos('Brightness', "Adjustments")

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
  cv2.namedWindow("Adjustments")
  cv2.createTrackbar('B/W Threshold', 'Adjustments', m.bw_threshold, 255, m.nothing)
  cv2.createTrackbar('Distort X', 'Adjustments', m.distort_x, 100, m.nothing)
  cv2.createTrackbar('Distort Y', 'Adjustments', m.distort_y, 100, m.nothing)
  cv2.createTrackbar('Distort Amount', 'Adjustments', m.distort_amount, 100, m.nothing)

  
  while success:

    success, frame = vc.read()
    sample_frame = frame[z.zones[0]['xy'][1]:z.zones[1]['xy'][1], z.zones[0]['xy'][0]:z.zones[1]['xy'][0]]
    board_frame = frame[z.zones[2]['xy'][1]:z.zones[3]['xy'][1], z.zones[2]['xy'][0]:z.zones[3]['xy'][0]]
    
    # Maintain callibration, updating periodically
    sample_frame, board_frame, board_frame_wb, update_sample = m.callibrate_frame(sample_frame, board_frame, 3)
    board_frame_clear = board_frame.copy()

    sample_frame = m.draw_hue_picker(sample_frame)

    mask_list = []

    # Clear board and start initalization each frame
    m.clear_board()

    for stage in range(1,PIECE_ARRAY_SIZE):
      s = m.selection[stage]
      # Periodically update sample hue
      if update_sample:
        s["hue"] = calc_hue(sample_frame, s["x"], s["y"])

      # If getting board corners
      board_frame_to_mask = board_frame_wb if stage == 1 else board_frame_clear
      mask_frame = color_mask(board_frame_to_mask, s["hue"], s["range"], s['brightness'], s['saturation'])
      s["centers"] = track(mask_frame)

      # Piece Type
      if stage > 1:
        s["pieces"], keep_backup = track_piece_side(board_frame_clear, s["centers"], s["backup"], s["hue"], board_frame)

        # If nothing has changed, prevent jittering
        if not keep_backup:
          s["backup"] = s["centers"]

        # Place pieces on the board
        board_frame = m.put_selection_on_board(board_frame, stage)

        mask_resized = cv2.resize(mask_frame, (150, 150), interpolation=cv2.INTER_AREA)
        mask_rgb = cv2.cvtColor(mask_resized, cv2.COLOR_GRAY2RGB)
        mask_list.append(mask_rgb)

    # # Wait to check required placement before beginning
    board_frame, valid_placement = m.wait_for_placement(board_frame) 
    if valid_placement:
      break;

    board_frame = cv2.resize(board_frame, (460, 460), interpolation=cv2.INTER_AREA)
    

    cv2.imshow("Samples", sample_frame)
    cv2.imshow("Board", board_frame)
    cv2.imshow("Masks", np.concatenate(mask_list, axis=1))
    m.bw_threshold = cv2.getTrackbarPos('B/W Threshold', "Adjustments")
    m.distort_x = cv2.getTrackbarPos('Distort X', "Adjustments")
    m.distort_y = cv2.getTrackbarPos('Distort Y', "Adjustments")
    m.distort_amount = cv2.getTrackbarPos('Distort Amount', "Adjustments")
    
    cv2.waitKey(100)

  print("Valid Now")
  return  

# Step 4: Starting WebSocket
def step_4(vc):

  app = FastAPI()
  loop_state = {
      "frame": None,
      "fen": ""
  }
  state_lock = threading.Lock()

  @app.websocket("/ws")
  async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
      last_video_time = 0
      last_fen_time = 0
      loop = asyncio.get_running_loop()
      while True:
        current_time = time.time()
        
        # Retrieve latest frame and FEN thread-safely
        with state_lock:
          current_frame = loop_state["frame"]
          current_fen = loop_state["fen"]

        # Send video frame every 50ms
        if current_time - last_video_time >= 0.05 and current_frame is not None:
          def encode_frame():
            success, buf = cv2.imencode(
                ".jpg", current_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            )
            return buf.tobytes() if success else None

          jpeg_bytes = await loop.run_in_executor(None, encode_frame)

          if jpeg_bytes:
            # Send as raw binary blob data
            await websocket.send_bytes(jpeg_bytes)
          last_video_time = current_time

        # Send partial FEN every 250ms
        if current_time - last_fen_time >= 0.2:
          await websocket.send_json({
              "type": "fen",
              "data": {"partialFen": current_fen}
          })
          last_fen_time = current_time

        await asyncio.sleep(0.01)
    except WebSocketDisconnect:
      pass
    except Exception:
      pass

  # Run FastAPI / Uvicorn in a background thread so OpenCV can control the main loop
  server_thread = threading.Thread(
      target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning", ssl_keyfile="key.pem", ssl_certfile="cert.pem"),
      daemon=True
  )
  server_thread.start()

  cv2.namedWindow("Parameters", cv2.WINDOW_NORMAL)
  # Initialize trackbars for every piece stage (from index 2 to end)
  for stage in range(2, len(m.selection)):
    s = m.selection[stage]
    piece_name = s["name"]
    cv2.createTrackbar(f"{piece_name} - Range", "Parameters", s["range"], 50, m.nothing)
    cv2.createTrackbar(f"{piece_name} - Bright", "Parameters", s["brightness"], 255, m.nothing)
    cv2.createTrackbar(f"{piece_name} - Sat", "Parameters", s["saturation"], 255, m.nothing)
    cv2.createTrackbar(f"{piece_name} - Offset", "Parameters", s["offset"], 150, m.nothing)

    
  # Create FastAPI with websocket
  # When connected, loop
  # Every 50ms, send a frame of board_frame to have message type 'video' and message.data.frame = <video frame>
  # Every 250ms, send a partial fen message.type = 'fen', message.data.partialFen = <data> 
  success = True
  while success:
   
    success, frame = vc.read()
    sample_frame = frame[z.zones[0]['xy'][1]:z.zones[1]['xy'][1], z.zones[0]['xy'][0]:z.zones[1]['xy'][0]]
    board_frame = frame[z.zones[2]['xy'][1]:z.zones[3]['xy'][1], z.zones[2]['xy'][0]:z.zones[3]['xy'][0]]
    
    # Maintain callibration, updating periodically
    sample_frame, board_frame, board_frame_wb, update_sample = m.callibrate_frame(sample_frame, board_frame, 3)
    board_frame_clear = board_frame.copy()

    sample_frame = m.draw_hue_picker(sample_frame)

    # Clear board and start initalization each frame
    m.clear_board()

    for stage in range(1,PIECE_ARRAY_SIZE):
      s = m.selection[stage]

      # Read live trackbar values for piece stages dynamically on every frame
      if stage >= 2:
        piece_name = s["name"]
        s["range"] = cv2.getTrackbarPos(f"{piece_name} - Range", "Parameters")
        s["brightness"] = cv2.getTrackbarPos(f"{piece_name} - Bright", "Parameters")
        s["saturation"] = cv2.getTrackbarPos(f"{piece_name} - Sat", "Parameters")
        s["offset"] = cv2.getTrackbarPos(f"{piece_name} - Offset", "Parameters")

      # Periodically update sample hue
      if update_sample:
        s["hue"] = calc_hue(sample_frame, s["x"], s["y"])

      # If getting board corners
      board_frame_to_mask = board_frame_wb if stage == 1 else board_frame_clear
      mask_frame = color_mask(board_frame_to_mask, s["hue"], s["range"], s['brightness'], s['saturation'])
      s["centers"] = track(mask_frame)

      # Piece Type
      if stage > 1:
        s["pieces"], keep_backup = track_piece_side(board_frame_clear, s["centers"], s["backup"], s["hue"], board_frame)

        # If nothing has changed, prevent jittering
        if not keep_backup:
          s["backup"] = s["centers"]

        # Place pieces on the board
        board_frame = m.put_selection_on_board(board_frame, stage)

    board_frame = cv2.resize(board_frame, (460, 460), interpolation=cv2.INTER_AREA)

    cv2.imshow("Board", board_frame)
    m.bw_threshold = cv2.getTrackbarPos('B/W Threshold', "Adjustments")
    m.distort_x = cv2.getTrackbarPos('Distort X', "Adjustments")
    m.distort_y = cv2.getTrackbarPos('Distort Y', "Adjustments")
    m.distort_amount = cv2.getTrackbarPos('Distort Amount', "Adjustments")

    board_matrix = m.board
    partial_fen = Board(board=board_matrix).to_fen()

    # Update shared state for the WebSocket broadcaster
    with state_lock:
      loop_state["frame"] = board_frame
      loop_state["fen"] = partial_fen

    cv2.waitKey(100)

  print("Game Over")

def step_test(vc):
  import logging
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger("WebSocketServer")

  app = FastAPI()
  loop_state = {
      "frame": None,
      "fen": ""
  }
  state_lock = threading.Lock()

  @app.websocket("/ws")
  async def websocket_endpoint(websocket: WebSocket):
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info(f"Client connection request received from {client_host}")
    
    await websocket.accept()
    logger.info(f"WebSocket connection successfully accepted for client: {client_host}")
    print("Connected to ", websocket)
    try:
      last_video_time = 0
      last_fen_time = 0
      loop = asyncio.get_running_loop()
      a = True
      
      while True:
        current_time = time.time()
        
        # Retrieve latest frame and FEN thread-safely
        with state_lock:
          current_frame = loop_state["frame"]
          current_fen = loop_state["fen"]

        # Send video frame every 50ms
        if current_time - last_video_time >= 0.05 and current_frame is not None:
          def encode_frame():
            success, buf = cv2.imencode(
                ".jpg", current_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            )
            return buf.tobytes() if success else None

          jpeg_bytes = await loop.run_in_executor(None, encode_frame)

          if jpeg_bytes:
            # Send as raw binary blob data
            await websocket.send_bytes(jpeg_bytes)
          last_video_time = current_time

        # Send partial FEN every 250ms
        if current_time - last_fen_time >= 0.25:
          
          await websocket.send_json({
              "type": "fen",
              "data": {"partialFen": current_fen if a else  "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR"}
          })
          a = not a
          last_fen_time = current_time

        await asyncio.sleep(0.01)
    except WebSocketDisconnect:
      logger.warning(f"WebSocket client disconnected cleanly: {client_host}")
    except Exception as e:
      logger.exception(f"Unexpected error in WebSocket endpoint with {client_host}")

  # Run FastAPI / Uvicorn in a background thread so OpenCV can control the main loop
  logger.info("Starting Uvicorn server thread on port 8000...")
  server_thread = threading.Thread(
      target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning"),
      daemon=True
  )
  server_thread.start()

  

  success = True
  while success:
    (success, frame) = vc.read()
    frame_vid = cv2.resize(frame, (460, 460), interpolation=cv2.INTER_AREA)
    # Update shared state for the WebSocket broadcaster
    with state_lock:
      loop_state["frame"] = frame_vid
      loop_state["fen"] = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

  
    cv2.waitKey(100)
      

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
  step_3(vc)
  step_4(vc)
  # step_test(vc)
  

if __name__=="__main__":
  main()
  

