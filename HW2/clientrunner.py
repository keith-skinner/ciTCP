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

if __name__ == '__main__':
    print('Welcome to TicTackToe\n')
    print(SPACING)
    pass
