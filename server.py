from http.server import HTTPServer

from io import StringIO
import json
from base_server import SimpleRequestHandler, get


class BattleshipRequestHandler(SimpleRequestHandler):


    @get("/name")
    def on_name(self):
        return self.send(200, "it works!!!")

    def on_get(self, path: str):
        return self.send(200, path)

    def on_post(self, path: str):
        pass

def run ():
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, BattleshipRequestHandler)
    httpd.serve_forever()


run()
