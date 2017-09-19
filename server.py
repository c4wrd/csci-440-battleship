import sys, json
from http.server import HTTPServer
from sserver import SimpleServer, get
from battleship.board import Board, load_board_from_file, serialize_board_to_str, HitResult

board = None # type: Board

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
