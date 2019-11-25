from random import randint
from citcp.header import Header
import citcp.common

#ciTCP Transmission Control Block
class Tcb:
    def __init__(self, sock, conn_addr = None):
        self.sock = sock
        self.conn_addr = conn_addr
        self.seq = randint(0, Header.Limits.MAX_SEQ.value-1)
        self.ack = 0
        self.sent = 0
        self.recv = 0
        self.timeout_wait = citcp.common.TIMEOUT_WAIT_DEFAULT