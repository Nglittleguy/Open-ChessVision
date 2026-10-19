from chess.pieces.piece_enums import PieceColor, PieceType

class Piece:

  def __init__(
      self, 
      color: PieceColor, 
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
    color = "White" if self.color == PieceColor.WHITE else "Black"
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
    return f'{color} {type} [{x}, {y}]'

  def fen_notation(self):
    letter = ""
    match self.type:
      case PieceType.KING:
        letter = "K"
      case PieceType.QUEEN:
        letter = "Q"
      case PieceType.ROOK:
        letter = "R"
      case PieceType.BISHOP:
        letter = "B"
      case PieceType.KNIGHT: 
        letter = "N"
      case PieceType.PAWN:
        letter = "P"

    if self.color == PieceColor.BLACK:
      letter = letter.lower()

    return letter
