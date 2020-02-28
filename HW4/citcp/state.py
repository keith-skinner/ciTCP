import logging
from enum import Enum, auto

class TCPState(Enum):
    CLOSED = auto()
    LISTEN = auto()
    SYN_SENT = auto()
    SYN_RECIEVED = auto()
    ESTABLISHED = auto()
    CLOSE_WAIT = auto()
    LAST_ACK = auto()
    FIN_WAIT_1 = auto()
    FIN_WAIT_2 = auto()
    TIME_WAIT = auto()

    @staticmethod
    def startingState():
        logging.info(f"State: --> {TCPState.CLOSED.name}")
        return TCPState.CLOSED

    def changeState(self, state):
        logging.info(f"State: {self.name} --> {state.name}")
        self = state
        return self