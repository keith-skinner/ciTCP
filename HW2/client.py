#!/usr/bin/env python3
import argparse, socket, logging
import protocol as Protocol
from common import recvall

# Uncomment the line below to print the INFO messages
# logging.basicConfig(level=logging.INFO)

class Client:

    def __init__(self, socket):
        self.socket = None
        self.sid = None
        self.gid = None
        self.role = None

    def connect(self):
        self.sid, reason = Protocol.ClientConnect(self.socket)
        if self.sid is None:
            self.socket.close()
            return False, reason
        return True, None

    def play(self):
        self.gid, self.role, reason = Protocol.ClientGame(self.socket, self.sid)
        if self.gid is None or self.sid is None:
            self.socket.close()
            return False, reason
        return True, None
    
    def playerMove(self, move):
        

    def oponentMove(self):
        pass

    def disconnect(self):
        pass

    def validateSID(self):
        pass

    def validateGID(self):
        pass



if __name__ == '__main__':
    port = 9001
    parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()
    