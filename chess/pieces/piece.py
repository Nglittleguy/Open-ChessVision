from chess.pieces.piece_enums import PieceColor, PieceType

class Piece:

  def __init__(
      self, color: PieceColor, 
      type: PieceType, 
      position: tuple[int, int], 
      hasMoved: bool = "False", 
      pawnDoubleStep: bool = "False"
  ):
    self.color = color
    self.type = type
    self.position = position
    self.hasMoved = hasMoved
    self.pawnDoubleStep = pawnDoubleStep

  def __repr__(self):
    color = "White" if self.color else "Black"
    type = "NULL"
    match self.type:
      case PieceType.KING:
        type = "King"
      case PieceType.QUEEN:
        type = "Queen"
      case PieceType.ROOK:
        type = "Rook"
      case PieceType.BISHOP:
        type = "Bishop"
      case PieceType.KNIGHT: 
        type = "Knight"
      case PieceType.PAWN:
        type = "Pawn"
    x = self.position[0]
    y = self.position[1]
    return f'{color} {type}: [{x}, {y}]'
