#!/usr/bin/env python3
import argparse, socket, logging
import protocol as Protocol

# Uncomment the line below to print the INFO messages
# logging.basicConfig(level=logging.INFO)

class Client:

    def __init__(self, socket):
        self.socket = None
        self.sid = None
        self.gid = None
        self.role = None

    def connect(self):
        self.sid, reason = Protocol.ClientRequestConnect(self.socket)
        if self.sid is None:
            self.socket.close()
            return False, reason
        return True, None

    def game(self):
        self.gid, self.role, reason = Protocol.ClientRequestGame(self.socket, self.sid)
        if self.gid is None or self.sid is None:
            self.socket.close()
            return False, reason
        return True, None
    
    def playerMove(self, move):
        return = Protocol.ClientRequestMove(self.socket, self.sid, self.gid, move)

    def oponentMove(self):
        move, reason = Protocol.ClientReceiveMove(self.socket, self.sid, self.gid)
        if move is None:
            self.socket.close()
            return None, reason
        return move, None

    def gameOver(self):
        return Protocol.ClientGameOver(self.socket, self.sid, self.gid)

    def disconnect(self):
        ClientSessionDisconnect(self.socket, self.sid)
        socket.close()

    def forfeit(self):
        return ClientGameDisconnect(self.socket, self.sid, self.gid)

    def validateSID(self):
        sid, reason = ClientValidateSID(self.socket, self.sid)
        if sid is None:
            return False, reason
        return True, None

    def validateGID(self):
        gid, reason = ClientValidateGID(self.socket, self.sid, self.gid)
        if gid is None:
            return False, reason
        return True, None


# if __name__ == '__main__':
#     port = 9001
#     parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
#     parser.add_argument('host', help='IP address of the server.')
#     args = parser.parse_args()
    