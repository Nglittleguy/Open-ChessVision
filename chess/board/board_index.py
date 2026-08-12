from chess.board.board import Board
from camera.tracking import BOARD_SIZE, BORDER_SIZE

def notation2xy(notation: str):
  col = notation[0]
  row = int(notation[1])

  assert col >= 'a' and col <= 'h' and row >= 1 and row <= 8, f"Notation if Out of Bounds: {notation}"

  x = ord(col) - ord('a')
  y = row - 1
  return (x,y)


def xy2notation(xy: tuple[int,int]):
  x = xy[0]
  y = xy[1]

  assert x >= 0 and x < 8 and y >= 0 and y < 8, f"XY if Out of Bounds: {xy}" 

  col = chr(ord('a')+x)
  row = str(y + 1)
  return f"{col}{row}"

def xy2tracking(xy: tuple[int, int]):
  full_dimension = BOARD_SIZE + BORDER_SIZE + BORDER_SIZE
  cell_dimension = BOARD_SIZE/8
  top_left = (int(BORDER_SIZE + (xy[0] * cell_dimension)), int(full_dimension - (BORDER_SIZE + (xy[1] + 1) * cell_dimension)))

  return top_left