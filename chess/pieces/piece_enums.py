from enum import Enum

class PieceType(Enum):
  KING = 7
  QUEEN = 6
  ROOK = 3
  BISHOP = 2
  PAWN = 1
  KNIGHT = 5
  NULL = 0

class PieceColor(Enum):
  WHITE = True
  BLACK = False