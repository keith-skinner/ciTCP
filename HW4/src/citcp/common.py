#!/usr/bin/env python3
import socket, logging

def recvall(sock, length):
    data = b''
    address = None
    while len(data) < length:
        more, address = sock.recvfrom(length - len(data))
        if not more:
            logging.error('Did not receive all the expected bytes from server.')
            break
        data += more
    return data, address

def send(socket, message):
    socket.sendall(message)
    logging.info('Sent: {}'.format(message))


def recv(socket, length):
    message = recvall(socket, length).decode('utf-8')
    logging.info('Received: {}'.format(message))
    return message