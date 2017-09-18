import sys

from http.server import HTTPServer
from sserver import SimpleServer, get
from battleship.board import Board, load_board_from_file

board = None # type: Board

class BattleshipRequestHandler(SimpleServer):


    @get("/opponent_board.html")
    def on_name(self):
        return self.send(200, "it works!!!")

    @get("/own_board.html")
    def handle_own_board(self):
        pass

    def on_get(self, path: str):
        return self.send(200, path)

    def on_post(self, path: str):
        pass

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
