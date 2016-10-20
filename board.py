PIECES = {
    'aircraft_carrier': {'name': 'Aircraft Carrier', 'spaces': 5},
    'battleship': {'name': 'Battleship', 'spaces': 4},
    'submarine': {'name': 'Submarine', 'spaces': 3},
    'destroyer': {'name': 'Destroyer', 'spaces': 3},
    'patrol_ship': {'name': 'Patrol Ship', 'spaces': 2}
}

"""COLUMNS can be extended, but should never contain a digit.
if .isdigit() returns true on any element within COLUMNS,
the code will break."""
COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
"""ROWS can be extended, but should only contain strings that
can be converted into digits. if .isdigit() returns false on
any elemnt in ROWS, the code will break.
Should also be ascending order, starting with 1,
and incrementing by 1."""
ROWS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
# len(COLUMNS) == len(ROWS) should always return True.
GRID = [(column + row) for column in COLUMNS for row in ROWS]
