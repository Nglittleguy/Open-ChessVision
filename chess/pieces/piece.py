from piece_enums import PieceColor, PieceType

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
