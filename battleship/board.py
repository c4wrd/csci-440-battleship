import os

class HitResult:
    OUT_OF_BOUNDS = 0
    ALREADY_HIT = 1
    MISS = 2
    SHIP_HIT = 3
    SHIP_SUNK = 4

class MarkerType:
    WATER = "_"
    HIT = "X"
    MISS = "O"
    CARRIER = "C"
    BATTLESHIP = "B"
    CRUISER = "R"
    SUBMARINE = "S"
    DESTROYER = "D"

    __ALL__ = [WATER, CARRIER, BATTLESHIP, CRUISER, SUBMARINE, DESTROYER, HIT, MISS]

    MAX_HITS = {
        CARRIER: 5,
        BATTLESHIP: 4,
        CRUISER: 3,
        SUBMARINE: 3,
        DESTROYER: 1
    }

    @staticmethod
    def is_valid(value: str):
        if value not in MarkerType.__ALL__:
            return False
        return True

class Board:

    def __init__(self, board):
        self.board = board
        self.hits = [[None for i in range(10)] for i in range(10)]
        self.ship_hits = self.load_hits()

    def load_hits(self):
        hits = {
            MarkerType.CARRIER: 0,
            MarkerType.BATTLESHIP: 0,
            MarkerType.CRUISER: 0,
            MarkerType.SUBMARINE: 0,
            MarkerType.DESTROYER: 0
        }

        for row in self.board:
            for char in row:
                if char != MarkerType.WATER:
                    hits[char] += 1
        return hits

    def attack(self, x, y):

        if x < 0 or y < 0 or x > 9 or y > 9:
            # out of bounds, no hit
            return {"result": HitResult.OUT_OF_BOUNDS}

        # if this has already been attempted
        if self.hits[x][y] is not None:
            return {"result": HitResult.ALREADY_HIT}

        # get the marker at this position
        marker = self.board[x][y]

        # if it is a ship
        if marker != MarkerType.WATER:
            self.ship_hits[marker] += 1
            self.hits[x][y] = marker
            if self.ship_hits[marker] == MarkerType.MAX_HITS[marker]:
                return {"result": HitResult.SHIP_SUNK, "ship_type": marker}
            else:
                return {"result": HitResult.SHIP_HIT}

        self.hits[x][y] = MarkerType.MISS
        return {"result": HitResult.MISS}

    def is_ship_sunk(self, x, y):
        """
        Determines whether or not a specific marker with a ship
        has been sunk when visually representing the board
        """
        marker = self.hits[x][y]
        total_hits = self.ship_hits[marker]
        return total_hits == MarkerType.MAX_HITS[marker]

    def is_position_hit(self, x, y):
        return self.hits[x][y]

    def create_opponent_board(self):
        board = [["_" for i in range(10)] for i in range(10)]
        for row in range(10):
            for col in range(10):
                marker = self.hits[row][col]
                if marker == MarkerType.MISS or marker == MarkerType.WATER:
                    board[row][col] = marker
                else:
                    if self.is_ship_sunk(row, col):
                        board[row][col] = marker
                    else:
                        board[row][col] = MarkerType.HIT

def save_board(board: Board, filename):
    serialized_rows = [str.join('', line) for line in board.board]
    serialized_board = str.join("\n", serialized_rows)

    if os.path.isfile(filename):
        os.remove(filename)

    with open(filename, "w+") as file:
        file.write(serialized_board)

def load_board_from_file(file_name):
    try:
        with open(file_name) as file:
            contents = file.read()
            rows = [[char for char in line] for line in contents.split("\n")]
            if len(rows) < 10:
                raise RuntimeError("Invalid number of rows in the board")
            for i in range(len(rows)):
                row = rows[i]
                if len(row) < 10:
                    raise RuntimeError("Invalid number of characters in row %d" % i)
                for char in row:
                    if not MarkerType.is_valid(char):
                        raise RuntimeError("Invalid character '%s' in row %d" % (char, i))

            return Board(rows)
    except FileNotFoundError:
        print("Invalid board file!")
        raise