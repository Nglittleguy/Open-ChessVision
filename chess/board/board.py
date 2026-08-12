from pieces.piece import Piece

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