import sys, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, ParseResult, parse_qsl

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
        self.markers = [[MarkerType.WATER for i in range(10)] for i in range(10)]
        self.ship_hits = self.load_hits()

    def load_hits(self):
        hits = {
            MarkerType.CARRIER: 0,
            MarkerType.BATTLESHIP: 0,
            MarkerType.CRUISER: 0,
            MarkerType.SUBMARINE: 0,
            MarkerType.DESTROYER: 0
        }

        return hits

    def attack(self, x, y):

        if x < 0 or y < 0 or x > 9 or y > 9:
            # out of bounds, no hit
            return {"result": HitResult.OUT_OF_BOUNDS}

        # if this has already been attempted
        if self.markers[x][y] is not MarkerType.WATER:
            return {"result": HitResult.ALREADY_HIT}

        # get the marker at this position
        marker = self.board[x][y]

        # if it is a ship
        if marker != MarkerType.WATER:
            self.ship_hits[marker] += 1
            self.markers[x][y] = marker
            if self.ship_hits[marker] == MarkerType.MAX_HITS[marker]:
                return {"result": HitResult.SHIP_SUNK, "ship_type": marker}
            else:
                return {"result": HitResult.SHIP_HIT}

        self.markers[x][y] = MarkerType.MISS
        return {"result": HitResult.MISS}

    def is_ship_sunk(self, x, y):
        """
        Determines whether or not a specific marker with a ship
        has been sunk when visually representing the board
        """
        marker = self.markers[x][y]
        total_hits = self.ship_hits[marker]
        return total_hits == MarkerType.MAX_HITS[marker]

    def create_opponent_board(self):
        board = [["_" for i in range(10)] for i in range(10)]
        for row in range(10):
            for col in range(10):
                marker = self.markers[row][col]
                if marker == MarkerType.MISS or marker == MarkerType.WATER:
                    board[row][col] = marker
                else:
                    if self.is_ship_sunk(row, col):
                        board[row][col] = marker
                    else:
                        board[row][col] = MarkerType.HIT
        return board

def serialize_board_to_str(board: [[str]]):
    serialized_rows = [str.join('', line) for line in board]
    serialized_board = str.join("\n", serialized_rows)
    return serialized_board

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

def parse(value: str):
    parsed = parse_qsl(value)
    return dict(parsed)

def get(path):
    def wrapper(method):
        SimpleServer.register_get(path, method)
        return method
    return wrapper

def post(path):
    def wrapper(method):
        SimpleServer.register_post(path, method)
        return method
    return wrapper

class SimpleServer(BaseHTTPRequestHandler):

    GET_ROUTES = {}
    POST_ROUTES = {}

    @staticmethod
    def register_get(path, method):
        SimpleServer.GET_ROUTES[path] = method

    @staticmethod
    def register_post(path, method):
        SimpleServer.POST_ROUTES[path] = method

    def __load_request__(self):
        """
        Loads basic information from the request,
        such as query parameters
        """
        self.raw_body = None
        self.str_body = None
        self.form_body = None
        self.parsed = urlparse(self.path)
        self.query_parameters = parse(self.parsed.query)

    def do_POST(self):
        self.__load_request__()
        if "Content-Length" in self.headers:
            size = int(self.headers["Content-Length"])
            self.raw_body = self.rfile.read(size)
            try:
                self.str_body = self.raw_body.decode("utf-8")
            except:
                pass

        if self.path in SimpleServer.POST_ROUTES:
            return SimpleServer.POST_ROUTES[self.path](self)
        else:
            return self.on_post(self.path)

    def do_GET(self):
        self.__load_request__()

        if self.path in SimpleServer.GET_ROUTES:
            return SimpleServer.GET_ROUTES[self.path](self)
        else:
            return self.on_get(self.path)

    def send_success(self, message):
        return self.send_response(200, message)

    def send(self, status_code: int, message: str = None, headers: dict = None):
        self.send_response(status_code)

        if headers is not None:
            for key, value in headers:
                self.send_header(key, value)
        self.end_headers()

        if message is not None:
            self.wfile.write(bytes(message, "utf8"))

    def has_form_value(self, param: str):
        """
        Returns whether or not a form value
        was present in the POST body.
        :param param:
        :return:
        """
        return param in self.get_body_as_form()

    def has_form_values(self, names: [str]):
        """
        Checks for multiple form values
        :param names: A list of form value names to check for
        :return: True if all of the form values are present, otherwise false
        """
        return all([self.has_form_value(value) for value in names])

    def form_value(self, name: str):
        if self.has_form_value(name):
            return self.get_body_as_form()[name]
        else:
            return None

    def has_query_param(self, param: str):
        """
        Returns whether or not a query parameter
        was present.
        :param param: The param to check for
        :return: True if it is set, otherwise False
        """
        return param in self.query_parameters

    def has_query_params(self, params: [str]):
        """
        :param params: A list of query parameters to check for
        :return: True if all of the parameters exist
        """
        return all([self.has_query_param(param) for param in params])

    def query_param(self, param: str):
        """
        Returns a query parameter
        :param param: The query parameter
        :return: The query parameter if it exists, otherwise None
        """
        if self.has_query_param(param):
            return self.query_parameters[param]
        else:
            return None

    def get_body_as_str(self):
        return self.str_body

    def get_body_as_form(self):
        if self.form_body is not None:
            return self.form_body
        self.form_body = parse(self.str_body)
        return self.form_body

    def on_get(self, path: str):
        """
        To be overridden in subclasses.
        :param path: The path of the request
        """
        raise NotImplementedError()

    def on_post(self, path: str):
        """
        To be overridden in subclasses.
        :param path: The path of the request
        :param body: The body of the POST request if it exists
        """
        raise NotImplementedError()

class BattleshipRequestHandler(SimpleServer):


    @get("/opponent_board.html")
    def on_name(self):
        opponent_view = board.create_opponent_board()
        opponent_view_str = serialize_board_to_str(opponent_view)
        return self.send(200, opponent_view_str)

    @get("/own_board.html")
    def handle_own_board(self):
        board_view = board.board
        board_view_str = serialize_board_to_str(board_view)
        return self.send(200, board_view_str)

    def on_get(self, path: str):
        return self.send(404, "Invalid path")

    def on_post(self, path: str):
        if self.has_form_values(["x", "y"]):
            x = int(self.form_value("x"))
            y = int(self.form_value("y"))
            response = board.attack(x, y)

            result = response["result"]

            if result == HitResult.OUT_OF_BOUNDS:
                return self.send(404)
            elif result == HitResult.ALREADY_HIT:
                return self.send(410)
            elif result == HitResult.MISS:
                return self.send(200, "hit=0")
            elif result == HitResult.SHIP_HIT:
                return self.send(200, "hit=1")
            elif result == HitResult.SHIP_SUNK:
                return self.send(200, "hit=1&sink=%s" % response["ship_type"])
            else:
                return self.send(500)
        else:
            self.send(400, "Invalid request. Expected [x,y] form content.")


board = None # type: Board

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Invalid number of arguments. Use 'python server.py [port] [board.txt]")

    port = int(sys.argv[1])
    board_str = sys.argv[2]

    global board
    board = load_board_from_file(board_str)

    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, BattleshipRequestHandler)
    httpd.serve_forever()
