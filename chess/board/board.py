from chess.pieces.piece import Piece
from camera.tracking import BOARD_SIZE, BORDER_SIZE, CELL_SIZE

class Board:

  def __init__(
        self, **kwargs
    ):
      board = [[None for _1 in range(8)] for _2 in range(8)]
      tempBoard = [[None for _1 in range(8)] for _2 in range(8)]
      isSize = True

      copy_board = kwargs['board']
      if copy_board and len(copy_board)>=8:
        for y in range(8):
           if len(copy_board[y]) != 8:
              isSize = False
              break
           for x in range(8):
              if copy_board[y][x] and isinstance(copy_board[y][x], Piece):
                p = copy_board[y][x]
                tempBoard[y][x] = Piece(p.color, p.type, (y,x), p.hasMoved, p.pawnDoubleStep)

      self.board = tempBoard if isSize else board

  def to_fen(self):
    output = ""
    for y in range(8):
      empty = 0

      for x in range(8):

        if self.board[x][7-y]:
          assert(isinstance(self.board[x][7-y], Piece), "Cell is neither null nor a Piece")

          if empty > 0:
              output += str(empty)
              empty = 0
          output += self.board[x][7-y].fen_notation()

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

def average_board(board_list):
  average = [[None for _1 in range(8)] for _2 in range(8)]
  count_board = [[0 for _1 in range(8)] for _2 in range(8)]

  for board in board_list:
    for x in range(8):
      for y in range(y):
        if board[x][y] == average[x][y]:
          count_board[x][y] += 1
        else:
          if count_board[x][y] == 0:
            average[x][y] = board[x][y]
            count_board[x][y] += 1
          else:
            count_board[x][y] -= 1

  return Board(board=average)

      
