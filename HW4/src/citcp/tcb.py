from numpy.random import randint
from citcp.header import Header

#ciTCP Transmission Control Block
class Tcb:
    def __init__(self, conn_addr):
        # Who you're connected to
        self.conn_addr = conn_addr
        # Starting numbers
        self.seq = randint(Header.Limits.MAX_SEQ.value)
        self.ack = 0
        # Bytes recieved and sent
        self.sent = 0
        self.recv = 0

    def setAck(self, ack):
        if ack < Header.Limits.MAX_ACK.value:
            self.ack = ack
    
    def addSent(self, sent):
        self.sent += sent

    def addRecv(self, recv):
        self.recv += recv

    def nextSeq(self, bytes=1):
        return self.seq + bytes
    
    def nextAck(self, bytes=1):
        return self.ack + bytes + 1
