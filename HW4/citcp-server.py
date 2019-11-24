import socket, logging, argparse
from citcp.header import Header
from citcp.state import TCPState
from citcp.common import *
from citcp.tcb import Tcb
from numpy.random import seed


def parseArgs():
    parser = argparse.ArgumentParser(prog="ciTCP-server", description="A ciTCP Server")
    parser.add_argument('port', help="port the server binds to", type=int)
    parser.add_argument('file', help="file the server sends")
    return parser.parse_args()


def initSocket(args):
    logging.info("Creating TCP/IP socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', args.port)
    logging.info(f"Binding socket to interface: {server_address[0]}:{server_address[1]}")
    sock.bind(server_address)
    return sock


# TODO: Error checking for exceptions
if __name__ == '__main__':
    args = parseArgs()
    seed(0xB429F2019)
    tcb = Tcb(initSocket(args))
    state = TCPState.startingState()
    
    while True:
        state = openResponderSequence(tcb, state)
        closed = sendFile(tcb, args.filename)
        if not closed:
            state = closeInitiatorSequence(tcb, state)
        else:
            state = closeResponderSequence(tcb, state)