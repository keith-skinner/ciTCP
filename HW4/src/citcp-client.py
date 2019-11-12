import socket, logging, sys, argparse
from citcp.header import Header
from numpy.random import seed, randint

# Milestone 1
#   High level design of client and server,
#     must be detailed and approved to continue.

# Milestone 2
#   Connection establishment and teardown.
#   Don't send any data
#   Assume no packet loss
#   No congestion window
#   No timers, retransmission, duplicate 
#     ack handling

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

if __name__ == '__main__':
    
    #python3 citcp-client.py IP-OR-HOSTNAME PORT-NUMBER FILE-NAME
    parser = argparse.ArgumentParser(prog='ciTCP-client', description='A ciTCP Client')
    parser.add_argument('hostname', help='The host to connect to')
    parser.add_argument('port', help='The port to connect to on the host')
    parser.add_argument('filename', help='The file to create locally')
    args = parser.parse_args()

    random.seed(0x429F2019+1)

    STATE = TCPState.CLOSED
    logging.info(f"State: {STATE.name}")

    logging.info("Create a UDP socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (args.hostname, args.port)
    sequence_number = random.random()
    logging.info(f"Initial Sequence Number for Client: {sequence_number}")

    seq_num = randint(0, Header.Limits.MAX_SEQ)
    window = 0
    ack_num = 0

    syn = Header.create(seq_num, ack_num, window, Header.Flags.SYN.value)
    seq_num += 1

    logging.info(f"Sent Header:\n{syn}")
    syn_data = syn.toBytes('big')
    logging.info(f"Sent Data: {syn_data}")
    sock.sendto(syn_data, address)

    STATE = TCPState.SYN_SENT
    logging.info(f"State: {STATE.name}")

    data, address = sock.recvfrom(Header.length())
    logging.info(f"Received Data: {data}")
    syn_ack = Header.fromBytes(data, 'big')
    logging.info(f"Received Header:\n{syn_ack}")

    #reject connection if corrupt or not syn
    if syn_ack.isCorrupted():
        logging.error(f"Message: Corrupted; State: {STATE.name}")
        exit() #TODO: retry
    
    if not syn_ack.getSYN() and not syn_ack.getACK() or syn_ack.getFIN():
        logging.error(f"Message: Incorrect Flags; State: {STATE.name}")
        exit() #TODO: retry

    ack_num = syn_ack.seq_num

    ack = Header.create(seq_num, ack_num, window, Header.Flags.ACK.value)

    logging.info(f"Sent Header:\n{ack}")
    ack_data = syn_ack.toBytes('big')
    logging.info(f"Sent Data: {ack_data}")
    sock.sendto(ack_data, address)

    STATE = TCPState.ESTABLISHED
    logging.info(f"State: {STATE.name}")

    ## RECV FILE HERE

    ## CLIENT HAPPENS TO BE FIN SENDER

    my_fin = Header.create(seq_num, ack_num, window, Header.Flags.FIN.value)
    
    logging.info(f"Sent Header:\n{my_fin}")
    my_fin_data = my_fin.toBytes('big')
    logging.info(f"Sent Data: {my_fin_data}")
    sock.sendto(my_fin_data, address)

    STATE = TCPState.FIN_WAIT_1
    logging.info(f"State: {STATE.name}")

    data, address = sock.recvfrom(Header.length())
    logging.info(f"Received Data: {data}")
    ack = Header.fromBytes(data)
    logging.info(f"Received Header: {data}")

    STATE = TCPState.FIN_WAIT_2
    logging.info(f"State: {STATE.name}")

    data, address = sock.recvfrom(Header.length())
    logging.info(f"Received Data: {data}")
    fin = Header.fromBytes(data)
    logging.info(f"Received Header: {data}")

    my_ack = Header.create(seq_num, ack_num, window, Header.Flags.ACK.value)

    STATE = TCPState.TIME_WAIT
    logging.info(f"State: {STATE.name}")

    STATE = TCPState.CLOSED
    logging.info(f"State: {STATE.name}")




    

