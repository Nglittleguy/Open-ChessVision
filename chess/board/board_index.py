from board import Board

def notation2xy(notation: str):
  col = notation[0]
  row = int(notation[1])

  assert col >= 'a' and col <= 'h' and row >= 1 and row <= 8, f"Notation if Out of Bounds: {notation}"
  
  x = ord(col) - ord('a')
  y = row - 1
  return (x,y)


def xy2notation(xy: tuple[int,int]):
  x = xy[0]
  y = xy[0]

  assert x >= 0 and x < 8 and y >= 0 and y < 8, f"XY if Out of Bounds: {xy}" 

  col = chr(ord('a')+x)
  row = str(y + 1)
  return f"{col}{row}"