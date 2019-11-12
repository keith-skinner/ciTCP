import socket, logging, argparse
from citcp.header import Header
from numpy.random import seed, randint
from enum import Enum, auto

#TODO change message size to some larger size and see if it blocks on that larger size or nah

class TCPState(Enum):
    CLOSED = auto()
    LISTEN = auto()
    SYN_SEND = auto()
    SYN_RECIEVED = auto()
    ESTABLISHED = auto()
    CLOSE_WAIT = auto()
    LAST_ACK = auto()
    FIN_WAIT_1 = auto()
    FIN_WAIT_2 = auto()
    TIME_WAIT = auto()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="ciTCP-server", description="ciTCP Server")
    parser.add_argument('port', help="port the server binds to", type=int)
    parser.add_argument('file', help="file the server sends")
    args = parser.parse_args()

    seed(19930603) # numpy.random seed

    STATE = TCPState.CLOSED
    logging.info(f"State: {STATE.name}")

    logging.info("Creating TCP/IP socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = ('localhost', args.port)
    logging.info(f"Binding socket to port {server_address[0]}:{server_address[1]}")
    sock.bind(server_address)

    while True:
        STATE = TCPState.LISTEN
        logging.info(f"State: {STATE.name}")

        logging.info("Waiting to receive connection")
        data, address = sock.recvfrom(Header.length())
        logging.info(f"Received Data: {data}")
        syn = Header.fromBytes(data, 'big')
        logging.info(f"Received Header:\n{syn}")

        #reject connection if corrupt or not syn
        if syn.isCorrupted():
            logging.error(f"Message: Corrupted; State: {STATE.name}")
            exit() #TODO: retry
        
        if not syn.getSYN() or syn.getACK() or syn.getFIN():
            logging.error(f"Message: Incorrect Flags; State: {STATE.name}")
            exit() #TODO: retry

        seq_num = randint(0, 2**16)
        ack_num = syn.seq

        syn_ack = Header()
        syn_ack.setSeqNum(seq_num).setAckNum(ack_num)
        syn_ack.setWindow(0).setChecksum(syn_ack.calcChecksum())
        syn_ack.setSYN().setACK()
        seq_num += 1

        logging.info(f"Sent Header:\n{syn_ack}")
        syn_ack_data = syn_ack.toBytes('big')
        logging.info(f"Sent Data: {syn_ack_data}")
        sock.sendto(syn_ack_data, address)

        STATE = TCPState.SYN_RECIEVED
        logging.info(f"State: {STATE.name}")
        
        data, address = sock.recvfrom(Header.length())
        logging.info(f"Received Data: {data}")
        ack = Header.fromBytes(data)
        logging.info(f"Received Header: {data}")

        #reject connection if corrupt or not ack
        if ack.isCorrupted():
            logging.error(f"Message: Corrupted; State: {STATE.name}")
            exit() #TODO: retry
        
        if not ack.getACK() or ack.getSYN() or ack.getFIN():
            logging.error(f"Message: Incorrect Flags: {ack.flags}; State: {STATE.name}")
            exit() #TODO: retry

        if not ack_num == ack.seq-1:
            logging.error(f"Message: Unexpected Sequence Number: {ack.seq}; State: {STATE.name}")
            exit() #TODO: retry

        ack_num += 1

        STATE = TCPState.ESTABLISHED
        logging.info(f"State: {STATE.name}")

        fin = None
        fin_received = False
        while not fin_received:
            data, address = sock.recvfrom(Header.length())
            logging.info(f"Received Data: {data}")
            fin = Header.fromBytes(data)
            logging.info(f"Received Header: {data}")

            if fin.getFIN() and not fin.getAck() and not fin.getSYN():
                fin_received = True
        
        fin_ack = Header()
        fin_ack.setSeqNum(seq_num).setAckNum(ack_num)
        fin_ack.setWindow(0).setChecksum(fin_ack.calcChecksum())
        fin_ack.setACK()
        seq_num += 1

        logging.info(f"Sent Header:\n{fin_ack}")
        fin_ack_data = fin_ack.toBytes('big')
        logging.info(f"Sent Data: {fin_ack_data}")
        sock.sendto(fin_ack_data, address)
        
        STATE = TCPState.CLOSE_WAIT
        logging.info(f"State: {STATE.name}")

        my_fin = Header()
        my_fin.setSeqNum(seq_num).setAckNum(ack_num)
        my_fin.setWindow(0).setChecksum(my_fin.calcChecksum())
        my_fin.setFin()

        logging.info(f"Sent Header:\n{my_fin}")
        my_fin_data = fin_ack.toBytes('big')
        logging.info(f"Sent Data: {my_fin_data}")
        sock.sendto(my_fin_data, address)

        STATE = TCPState.CLOSED