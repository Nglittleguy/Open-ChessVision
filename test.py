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

  @app.get("/")
  async def root():
    return "Hello world"
  
  # Run FastAPI / Uvicorn in a background thread so OpenCV can control the main loop
  logger.info("Starting Uvicorn server thread on port 8000...")
  server_thread = threading.Thread(
      target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning", ssl_keyfile="key.pem", ssl_certfile="cert.pem"),
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

  step_test(vc)
  

if __name__=="__main__":
  main()
  
