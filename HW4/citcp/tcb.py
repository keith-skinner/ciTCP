from numpy.random import randint
from citcp.header import Header
from citcp.common import TIMEOUT_WAIT_DEFAULT

#ciTCP Transmission Control Block
class Tcb:
    def __init__(self, sock):
        self.sock = sock
        self.seq = randint(Header.Limits.MAX_SEQ.value)
        self.ack = 0
        self.conn_addr = 0
        self.sent = 0
        self.recv = 0
        self.timeout_wait = TIMEOUT_WAIT_DEFAULT
