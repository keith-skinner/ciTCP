import socket, logging, random, sys, argparse
from citcp-header import Header

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

if __name__ == '__main__':
    random.seed(0x429F2019)

    #python3 citcp-client.py IP-OR-HOSTNAME PORT-NUMBER FILE-NAME
    parser = argparse.ArgumentParser(description='A ciTCP Client')
    parser.add_argument('hostname', help='The host to connect to')
    parser.add_argument('port', help='The port to connect to on the host')
    parser.add_argument('filename', help='The file to create locally')
    args = parser.parse_args()

    logging.info("Create a UDP socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (args.hostname, args.port)
    sequence_number = random.random()
    logging.info(f"Initial Sequence Number for Client: {sequence_number}")

    