from chess.pieces.piece import Piece
from camera.tracking import BOARD_SIZE, BORDER_SIZE, CELL_SIZE
import cv2

class Board:

  def __init__(
        self, **kwargs
    ):
      board = [[None]*8]*8
      tempBoard = [[None]*8]*8
      isSize = True

      copy_board = kwargs.get['board']
      if copy_board and len(copy_board>=8):
        for x in range(8):
           if len(copy_board[x]) >= 8:
              isSize = False
              break
           for y in range(8):
              if copy_board[x][y] and isinstance(copy_board[x][y], Piece):
                p = copy_board[x][y]
                tempBoard[x][y] = Piece(p.color, p.type, (x,y), p.hasMoved, p.pawnDoubleStep)

      self.board = tempBoard if isSize else board

# Draws board cells
def draw_board(frame):
  for x in range(8):
    for y in range(8):
      cv2.rectangle(frame, (BORDER_SIZE+x*CELL_SIZE, BORDER_SIZE+y*CELL_SIZE), (BORDER_SIZE+(x+1)*CELL_SIZE, BORDER_SIZE+(y+1)*CELL_SIZE), (150, 0, 255), 1)
  return frame