import socket, logging, argparse
from citcp.header import Header
from citcp.state import TCPState
from citcp.common import *
from citcp.tcb import Tcb
from numpy.random import seed

#TODO change message size to some larger size and see if it blocks on that larger size or nah

tcb = None

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


def ciTcpInit(seedVal, args):
    seed(seedVal)
    sock = initSocket(args)
    return sock

def ListenAction(sock):

    flags = None
    
    while True:
        syn_header, _, address = recv(sock)
        tcb = Tcb(address)
        tcb.ack = syn_header.ack

        if not syn_header.getSYN():
            continue

        ack_num = tcb.nextAck()
        flags = Header.Flags.SYN.value | Header.Flags.ACK.value
        
        syn_ack_header = Header.create(seq_num, ack_num, window, flags)
        headerSend(sock, address, syn_ack_header)

    return address, seq_num, ack_num, window, flags
    
def SynReceivedAction(sock):
    while True:
        ack_header, _, _ = recv(sock)
        if not ack_header.getACK():
            continue


# TODO: Error checking for exceptions
if __name__ == '__main__':
    args = parseArgs()
    state = TCPState.CLOSED
    logging.info(f"State: {state.name}")
    sock = ciTcpInit(0x429F2019, args)

    while True:
        state.changeState(TCPState.LISTEN)
        address, seq_num, ack_num, window, flags = ListenAction(sock)

        state.changeState(TCPState.SYN_RECIEVED)

        state = state.changeState(TCPState.ESTABLISHED)
        
        ## SEND FILE HERE

        file = open(args.file, "rb")
    
        closed = False
        while not closed:
            message = file.read(PAYLOAD_SIZE)
            if message == "":
                break

            seq_num += PAYLOAD_SIZE
            flags = Header.Flags.SYN.value
            syn_data = Header.create(seq_num, ack_num, window, flags)
            dataSend(sock, address, syn_data, message)

            header, payload, address = recv(sock)
            if header.getFIN():
                closed = True
            
        file.close()

        
        if not closed:
            initiatorSequence(sock, seq_num, ack_num, window, state)
        else:
            responderSequence(sock, address, seq_num, ack_num, window, state)
        
        