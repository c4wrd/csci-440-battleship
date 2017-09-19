import requests
from urllib.parse import parse_qsl

def run():
    import sys
    if len(sys.argv) < 5:
        print("Need IP, port, x coordinate and y coordinate")
    ip = sys.argv[1]
    port = int(sys.argv[2])
    xcoord = int(sys.argv[3])
    ycoord = int(sys.argv[4])
    serve_url = "http://%s:%d" %(ip, port)
    fire_command(serve_url, xcoord, ycoord)

def fire_command(serve_url, x, y):
    data = dict(x = x, y = y)

    resp = requests.post(serve_url, data)

    if resp.status_code == 200:
        content = dict(parse_qsl(resp.text))
        if content["hit"] == 0:
            print("Miss!")
        else:
            if "sunk" in content:
                print("You sunk a ship!")
            else:
                print("You hit a ship!")
    elif resp.status_code == 404:
        print("The location you entered was not a valid location!")
    elif resp.status_code == 410:
        print("You already guessed that!")
    if resp.status_code == 500:
        print("Unknown error occurred...")

    board = retrieve_board(serve_url)
    print(board)

def retrieve_board(serve_url):
    resp = requests.get(serve_url + "/opponent_board.html")
    return resp.text

run()