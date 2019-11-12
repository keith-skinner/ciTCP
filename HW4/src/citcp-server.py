import socket, logging, argparse
from citcp.header import Header
from numpy.random import seed, randint
from enum import Enum, auto

#TODO change message size to some larger size and see if it blocks on that larger size or nah

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


def parseArgs():
    parser = argparse.ArgumentParser(prog="ciTCP-server", description="A ciTCP Server")
    parser.add_argument('port', help="port the server binds to", type=int)
    parser.add_argument('file', help="file the server sends")
    return parser.parse_args()

def changeState(STATE):
    logging.info(f"State: {STATE.name}")
    return STATE

def initSocket(args):
    logging.info("Creating TCP/IP socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = ('localhost', args.port)
    logging.info(f"Binding socket to port {server_address[0]}:{server_address[1]}")
    sock.bind(server_address)
    return sock

def recv(sock):
    logging.info("Waiting to receive connection")
    data, address = sock.recvfrom(Header.length())
    logging.info(f"Received Data: {data}")
    h = Header.fromBytes(data, 'big')
    logging.info(f"Received Header:\n{h}")
    return h, address

def firstRecv(sock):
    syn, address = recv(sock)
    #create starter variables
    seq_num = randint(0, Header.Limits.MAX_SEQ.value)
    ack_num = syn.seq
    window = 0
    return address, seq_num, ack_num, window

def dataSend(sock, header, data):
    pass

def headerSend(sock, header):
    logging.info(f"Sent Header:{header}")
    header_raw = header.toBytes('big')
    logging.info(f"Sent Data: {header_raw}")
    sock.sendto(header_raw, address)

def send(sock, header, data):
    if data is None:
        headerSend(sock, header)
    else:
        dataSend(sock, header, data)

def ciTcpInit(seedVal):
    args = parseArgs()
    seed(seedVal)
    state = changeState(TCPState.CLOSED)
    sock = initSocket(args)
    return state, sock
    
# TODO: Error checking for exceptions
if __name__ == '__main__':
    state, sock = ciTcpInit(0x429F2019)

    while True:
        state = changeState(TCPState.LISTEN)
        address, seq_num, ack_num, window = firstRecv(sock)

        flags = Header.Flags.SYN.value | Header.Flags.ACK.value
        syn_ack = Header.create(seq_num, ack_num, window, flags)
        send(sock, syn_ack, None)

        state = changeState(TCPState.SYN_RECIEVED)
        
        ack, address = recv(sock)
        
        state = changeState(TCPState.ESTABLISHED)
        
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