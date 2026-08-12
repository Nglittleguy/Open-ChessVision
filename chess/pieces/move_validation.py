from chess.pieces.piece_enums import PieceColor, PieceType
from chess.pieces.piece import Piece
import numpy as np

def within_bounds (position: tuple[int,int]):
  return position[0] >= 0 and position[0] < 8 and position[1] >= 0 and position[1] < 8

def checking_validation(piece: Piece | None, turn: PieceColor, danger_types: list[PieceType]):
  if not piece:
    return 0  # continue
  if piece.color == turn:
    return 1  # stop
  if piece.type not in danger_types:
    return 1  # stop
  return 2 # add as check

# Check for orthognal checks (Rook, Queen)
def rook_check(king_pos, board: list[list[Piece]], turn: PieceColor):
  check = []
  # Same X axis
  for i in range(king_pos[0]+1,8):
    check_piece = board[i][king_pos[1]]
    res = checking_validation(check_piece, turn, [PieceType.ROOK, PieceType.QUEEN])
    if res == 0:
      continue
    elif res == 1:
      break
    check.append((i,king_pos[1]))

  for i in range(king_pos[0]-1,-1,-1):
    check_piece = board[i][king_pos[1]]
    res = checking_validation(check_piece, turn, [PieceType.ROOK, PieceType.QUEEN])
    if res == 0:
      continue
    elif res == 1:
      break
    check.append((i,king_pos[1]))

  # Same Y axis
  for i in range(king_pos[1]+1,8):
    check_piece = board[king_pos[0]][i]
    res = checking_validation(check_piece, turn, [PieceType.ROOK, PieceType.QUEEN])
    if res == 0:
      continue
    elif res == 1:
      break
    check.append((i,king_pos[1]))

  for i in range(king_pos[1]-1,-1,-1):
    check_piece = board[king_pos[0]][i]
    res = checking_validation(check_piece, turn, [PieceType.ROOK, PieceType.QUEEN])
    if res == 0:
      continue
    elif res == 1:
      break
    check.append((i,king_pos[1]))

  return check

# Check for diagonal checks (Bishop, Queen)
def bishop_check(king_pos, board: list[list[Piece]], turn: PieceColor):
  check = False
  dir = [(1,1), (-1,-1), (-1,1), (1,-1)]
  for d in dir:
    for i in range(1,8):
      pos_mod = tuple(i*x for x in d)
      check_pos = np.add(king_pos, pos_mod)
      if not within_bounds(check_pos):
        break
      check_piece = board[check_pos[0]][check_pos[1]]
      res = checking_validation(check_piece, turn, [PieceType.BISHOP, PieceType.QUEEN])
      if res == 0:
        continue
      elif res == 1:
        break
      check.append(check_pos)
  return check


# Check for local checks (King, Pawn, Knight)
def local_check(king_pos, board: list[list[Piece]], turn: PieceColor):
  checks = []
  local_dir = [
    {
      "pos_mod": (1,1),
      "pieces": [PieceType.PAWN, PieceType.KING],
    },
    {
      "pos_mod": (1,0),
      "pieces": [PieceType.KING],
    },
    {
      "pos_mod": (1,-1),
      "pieces": [PieceType.KING],
    },
    {
      "pos_mod": (0,-1),
      "pieces": [PieceType.KING],
    },
    {
      "pos_mod": (-1,-1),
      "pieces": [PieceType.KING],
    },
    {
      "pos_mod": (-1,0),
      "pieces": [PieceType.KING],
    },
    {
      "pos_mod": (-1,1),
      "pieces": [PieceType.PAWN, PieceType.KING],
    },
    {
      "pos_mod": (2,-1),
      "pieces": [PieceType.KNIGHT],
    },
    {
      "pos_mod": (2,1),
      "pieces": [PieceType.KNIGHT],
    },
    {
      "pos_mod": (1,2),
      "pieces": [PieceType.KNIGHT],
    },
    {
      "pos_mod": (1,-2),
      "pieces": [PieceType.KNIGHT],
    },
    {
      "pos_mod": (-1,2),
      "pieces": [PieceType.KNIGHT],
    },
    {
      "pos_mod": (-1,-2),
      "pieces": [PieceType.KNIGHT],
    },
    {
      "pos_mod": (-2,1),
      "pieces": [PieceType.KNIGHT],
    },
    {
      "pos_mod": (-2,-1),
      "pieces": [PieceType.KNIGHT],
    }
    
  ]

  for square in local_dir:
    check_pos = np.add(king_pos, square["pos_mod"]) if turn else np.subtract(king_pos, square["pos_mod"])
    if within_bounds[check_pos]:
      if board[check_pos[0]][check_pos[1]] and board[check_pos[0]][check_pos[1]].type in square["pieces"] and board[check_pos[0]][check_pos[1]].color != turn:
        checks.append(check_pos)

  return checks


# Does moving a piece (not the King) reveal your King to a check
def move_non_king_valid(king_pos, past_piece_pos, board: list[list[Piece]], turn:PieceColor):
  king_square:Piece = board[king_pos[0]][king_pos[1]]
  assert turn == king_square.color, "Wrong team for this move"
  assert king_square.type == PieceType.KING, "King in wrong place"

  # Same X or Y axis
  if past_piece_pos[0] == king_square[0] or past_piece_pos[1] == king_square[1]:
    checks = rook_check(king_pos, board, turn)

  # Same diagonal
  elif abs(past_piece_pos[0]-king_square[0]) == abs(past_piece_pos[1]-king_square[1]):
    checks = bishop_check(king_pos, board, turn)

  return checks

# Does moving the King put it in check
def move_king_valid(king_pos, turn:PieceColor, board:list[Piece]):
  king_square:Piece = board[king_pos[0]][king_pos[1]]
  assert turn == king_square.color, "Wrong team for this move"
  assert king_square.type == PieceType.KING, "King in wrong place"

  checks = []
  checks.append(rook_check(king_pos, board, turn))
  checks.append(bishop_check(king_pos, board, turn))
  checks.append(local_check(king_pos, board, turn))

  return checks