#!/usr/bin/env python3
import socket, logging
from citcp.header import Header
from citcp.state import TCPState

MSG_SIZE = 1024
PAYLOAD_SIZE = MSG_SIZE - Header.LENGTH

def rawSend(sock, address, header, data=b''):
    logging.info(f"Sending:")
    logging.info(f"\tHeader: {header}")
    logging.info(f"\tData: {data}")
    sock.sendto(header+data, address)

def headerSend(sock, address, header):
    logging.info(f"Sending:")
    logging.info(f"{header}")
    header_raw = header.to_bytes('big')
    rawSend(sock, address, header_raw)

def dataSend(sock, address, header, data):
    logging.info(f"Sending:")
    logging.info(f"{header}")
    logging.info(f"{data}")
    header_raw = header.to_bytes('big')
    data_raw = header.to_bytes('big')
    rawSend(sock, address, header_raw, data_raw)

def recv(sock):
    logging.info("Waiting to receive connection")
    data, address = sock.recvfrom(MSG_SIZE)
    logging.info(f"Received Data: {data}")
    header = Header.from_bytes(data[:Header.LENGTH], 'big')
    payload = data[Header.LENGTH:]
    logging.info(f"Received Header:\n{header}")
    return header, payload, address

def initiatorSequence(sock, address, seq_num, ack_num, window, state):
    #TODO
    pass

def responderSequence(sock, address, seq_num, ack_num, window, state):
    
    flags = Header.Flags.ACK.value
    fin_ack_header = Header.create(seq_num, ack_num, window, flags)
    headerSend(sock, address, fin_ack_header)

    state.changeState(TCPState.CLOSE_WAIT)

    ## CLOSE APPLICATION HERE

    flags = Header.Flags.FIN.value
    my_fin_header = Header.create(seq_num, ack_num, window, flags)
    headerSend(sock, address, my_fin_header)

    state.changeState(TCPState.CLOSED)