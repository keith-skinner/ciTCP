import socket, logging, sys, argparse
from random import seed
from citcp.header import Header
from citcp.state import TCPState
from citcp.common import *
from citcp.state import TCPState
from citcp.tcb import Tcb

# Uncomment the line below to print the INFO messages
logging.basicConfig(level=logging.INFO)

def parseArgs():
    parser = argparse.ArgumentParser(prog='ciTCP-client', description='A ciTCP Client')
    parser.add_argument('hostname', help='The host to connect to')
    parser.add_argument('port', help='The port to connect to on the host')
    parser.add_argument('filename', help='The file to create locally')
    return parser.parse_args()

def socketInit():
    logging.info("Creating UDP/IP socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock

def seedNum(s):
    logging.info(f"Using seed: {s}")
    seed(s)

if __name__ == '__main__':
    args = parseArgs()
    seedNum(0xA429F2019)
    tcb = Tcb(socketInit(), (args.hostname, int(args.port)))
    logging.info(f"Sequence Number: {tcb.seq}")

    state = openInitiatorSequence(tcb, None)
    receiveFile(tcb, args.filename)
    state = closeResponderSequence(tcb, state)
