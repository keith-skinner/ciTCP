import socket, logging, sys, argparse
from numpy.random import seed, randint
from citcp.header import Header
from citcp.state import TCPState
from citcp.common import *
from citcp.state import TCPState
from citcp.tcb import Tcb

def parseArgs():
    parser = argparse.ArgumentParser(prog='ciTCP-client', description='A ciTCP Client')
    parser.add_argument('hostname', help='The host to connect to')
    parser.add_argument('port', help='The port to connect to on the host')
    parser.add_argument('filename', help='The file to create locally')
    return parser.parse_args()

def receiveFile(tcb, filename):
    with open(filename, 'wb') as file:
        closed = False
        while not closed:
            payload, closed = recvData(tcb)
            file.write(payload)
            if not closed:
                sendHeader(tcb, Header.from_tcb(tcb, Header.FLags.ACK.value))

if __name__ == '__main__':
    
    #Init here
    args = parseArgs()
    seed(0x429F2019+1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tcb = Tcb(sock, (args.hostname, args.port))

    state = TCPState.startingState()
    state = openInitiatorSequence(tcb, state)
    receiveFile(tcb, args.filename)
    state = closeResponderSequence(tcb, state)
