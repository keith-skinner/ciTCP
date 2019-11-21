#!/usr/bin/env python3
import socket, logging

MSG_SIZE = 1024

def rawSend(sock, header, data=b''):
    logging.info(f"Sending:")
    logging.info(f"\tHeader: {header}")
    logging.info(f"\tData: {data}")
    sock.sendto(header+data, address)

def headerSend(sock, header):
    logging.info(f"Sending:")
    logging.info(f"{header}")
    header_raw = header.to_bytes('big')
    rawSend(sock, header_raw)

def dataSend(sock, header, data):
    logging.info(f"Sending:")
    logging.info(f"{header}")
    logging.info(f"{data}")
    header_raw = header.to_bytes('big')
    data_raw = header.to_bytes('big')
    rawSend(sock, header_raw, data_raw)

def recv(sock):
    logging.info("Waiting to receive connection")
    data, address = sock.recvfrom()
    logging.info(f"Received Data: {data}")
    header = Header.fromBytes(data[:Header.LENGTH], 'big')
    payload = data[Header.LENGTH:]
    logging.info(f"Received Header:\n{h}")
    return header, payload, address