import socket, logging, argparse
from citcp.header import Header
from numpy.random import seed, randint
from citcp.state import TCPState
from common import *

#TODO change message size to some larger size and see if it blocks on that larger size or nah

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
    seq_num, ack_num, window, flags = 0, 0, 0, 0
    
    while True:
        # Recieve SYN
        syn, address = recv(sock)
        if not syn.getSYN():
            continue

        # Create Header values for SYN + ACK
        seq_num = randint(0, Header.Limits.MAX_SEQ.value)
        ack_num = syn.seq + 1
        window = 0
        flags = Header.Flags.SYN.value | Header.Flags.ACK.value

        # Send Header
        syn_ack = Header.create(seq_num, ack_num, window, flags)
        headerSend(sock, syn_ack)
    return seq_num, ack_num, window, flags
    
def SynReceivedAction(sock):
    while True:
    ack, address = recv(sock)


# TODO: Error checking for exceptions
if __name__ == '__main__':
    args = parseArgs()
    state = TCPState.CLOSED
    logging.info(f"State: {state.name}")
    sock = ciTcpInit(0x429F2019, args)

    while True:
        state.changeState(TCPState.LISTEN)
        seq_num, ack_num, window, flags = ListenAction(sock)

        state.changeState(TCPState.SYN_RECIEVED)

        
        state = state.changeState(TCPState.ESTABLISHED)
        
        ## SEND FILE HERE

        ## SERVER HAPPENS TO BE FIN RECIEVER

        fin, address = recv(sock)

        flags = Header.Flags.ACK.value
        fin_ack = Header.create(seq_num, ack_num, window, flags)
        send(sock, fin_ack, None)

        state = changeState(TCPState.CLOSE_WAIT)

        flags = Header.Flags.FIN.value
        my_fin = Header.create(seq_num, ack_num, window, flags)
        send(sock, my_fin, None)

        state = changeState(TCPState.CLOSED)