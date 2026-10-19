from chess.pieces.piece import Piece
from camera.tracking import BOARD_SIZE, BORDER_SIZE, CELL_SIZE

class Board:

  def __init__(
        self, **kwargs
    ):
      board = [[None for _1 in range(8)] for _2 in range(8)]
      tempBoard = [[None for _1 in range(8)] for _2 in range(8)]
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

  def to_fen(self):
    output = ""
    for rank in self.board:
      empty = 0

      for cell in rank:

        if cell:
          assert(isinstance(cell, Piece), "Cell is neither null nor a Piece")

          if empty > 0:
              output += str(empty)
              empty = 0
          output += cell.fen_notation()

        else:
            empty = empty + 1

      if empty > 0:
          output += str(empty)
          
      output += "/"
    return output[:-1]
    
        

# Draws board cells
def draw_board(frame, cv2):
  for x in range(8):
    for y in range(8):
      cv2.rectangle(frame, (BORDER_SIZE+x*CELL_SIZE, BORDER_SIZE+y*CELL_SIZE), (BORDER_SIZE+(x+1)*CELL_SIZE, BORDER_SIZE+(y+1)*CELL_SIZE), (150, 0, 255), 1)
  return frame