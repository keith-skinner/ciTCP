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

def socketInit():
    socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket

if __name__ == '__main__':
    args = parseArgs()
    seed(0xA429F2019)
    tcb = Tcb(socketInit())
    tcb.conn_addr = (args.hostname, args.port)

    state = openInitiatorSequence(tcb, None)
    receiveFile(tcb, args.filename)
    state = closeResponderSequence(tcb, state)
