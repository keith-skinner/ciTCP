import argparse, socket, logging
from client import Client
from engine import Engine

HOST = '127.0.0.1'
POST = 8080

SPACING = '\n=\n'*20

def connectToServer(host, port):
    try:
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.connect((host, port))
        logging.info('Connect to server: ' + host + ' on port: ' + str(port))
        return socket
    except:
        return None

def makeMove(user, game):
    move = input("Move (1-9): ")
    user.move(int(move))
    if game.is_move_valid(move):
        if user.move(move):
            turn = not game.make_move(move)
            print(game)

if __name__ == '__main__':
    print('Welcome to TicTackToe\n')
    print(SPACING)

    socket = connectToServer(HOST, PORT)
    if socket is None:
        logging.error(f'Cannot connect to {HOST} on port {PORT}')
        exit(1)

    user = Client(socket)

    print('Connecting to server')
    sucess, reason = user.connect()
    if not sucess:
        logging.error(f'Client refused by Server: {reason}')
        exit(2)
    
    print('Connecting to game')
    sucess, reason = user.play()
    if not sucess:
        logging.error(f'Client refused by Server: {reason}')
        exit(3)

    game = Engine()

    print('Connected to game' + user.gid)
    print(SPACING)

    # X goes first
    bool turn = False
    if user.role == 'X':
        turn = True
    
    while not game.is_game_over():
        if turn:
            while turn:
                try:
                    makeMove(user, game)
                except:
                    pass
        while not turn:
            try:
                
            except:
                pass


        


