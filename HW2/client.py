#!/usr/bin/env python3
import argparse, socket, logging
from protocol import Protocol
from common import recvall

# Uncomment the line below to print the INFO messages
# logging.basicConfig(level=logging.INFO)



class Client:

    def __init__(self):
        self.sid = 0
        self.gid = 0
        self.socket = None


    def connect(self, host):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))
        logging.info('Connect to server: ' + host + ' on port: ' + str(port))
        self.sid = Protocol.connect(self.socket)

if __name__ == '__main__':
    port = 9001
    parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()
    