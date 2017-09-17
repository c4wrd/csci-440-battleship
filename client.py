import requests

def run():
    import sys
    if len(sys.argv) < 5:
        print("Need IP, port, x coordinate and y coordinate")
    ip = sys.argv[1]
    port = int(sys.argv[2])
    xcoord = int(sys.argv[3])
    ycoord = int(sys.argv[4])
    serve_url = "%s:%d" %(ip, port)
    fire_command(serve_url, xcoord, ycoord)

def fire_command(serve_url, x, y):
    data = dict(x = x, y = y)

    resp = requests.post(serve_url, data)
    #TODO
    #finish board interactions

def retrieve_board(serve_url):
    resp = requests.get(serve_url + "/opponent_board.html")
    print(resp.text)

run()