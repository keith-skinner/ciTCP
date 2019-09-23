#!/usr/bin/env python3
import socket, logging
from common import recvall

#General Responses
CONNECT = 'CONN'
DISCONNECT = 'DCON'
REJECT = 'RJCT'
CONFIRM = 'CONF'
END_GAME = 'ENDG'
#Requests / Response
TURN = 'TURN'
PLAY = 'PLAY'
CSID = 'CSID'
SID_LEN = 4
GID_LEN = 4
CODE_LEN = 4
ROLE_LEN = 1


def send(socket, message):
    socket.sendall(message)
    logging.info(f'Sent: {message}')


def recv(socket, length):
    message = recvall(socket, length).decode('utf-8')
    logging.info(f'Received: {message}')
    return message


def rejected(message):
    if message.startswith(REJECT):
        logging.info('Rejected from server: '+ message)
        return True
    return False


def expectedCode(message, expected):
    if not message.startswith(expected):
        logging.error('Recieved bad message from server:')
        logging.error('    Expected: ' + expected)
        logging.error('    Recieved: ' + message)
        return False
    return True


def getCode(message):
    return splitMessage(message)[0]


def getCSID(message):
    return splitMessage(message)[1]


def getGID(message):
    return splitMessage(message)[2]


def getRole(message):
    return splitMessage(message)[3]


def splitMessage(message):
    return message.split(':')


def createMessage(*argv):
    return (':'.join(argv)).encode()


def clientRequestConnect(socket):
    # TODO: change pdf to not make redundent checks to server
    message = createMessage(CONNECT)
    send(socket, message)
    message = recv(socket, CODE_LEN + 1 + SID_LEN)
    
    if rejected(message) or not expectedCode(message, CONNECT):
        return None
    csid = getCSID(message)
    return csid


def clientCheckCSID(socket, csid):
    message = createMessage(CSID, csid)
    send(socket, message)
    message = recv(socket, CODE_LEN)
    if rejected(message) or not expectedCode(message, CONFIRM):
        return None
    return csid


def clientRequestGame(socket, csid):
    #Send Play Request
    message = createMessage(PLAY, csid)
    send(socket, message)
    
    #Confirm Play Request
    length = CODE_LEN + 1 + SID_LEN
    message = recv(socket, length)
    if len(message) != length:
        return None, None
    if rejected(message):
        return None, None
    if not expectedCode(message, PLAY):
        return None, None
    if not expectedCode(getCSID(message), csid):
        return None, None
    
    #Init Game
    length = CODE_LEN+1+SID_LEN+1+GID_LEN+1+ROLE_LEN
    message = recv(socket, length)
    if len(message) != length:
        return None, None
    if rejected(message):
        return None, None
    if not expectedCode(message, PLAY):
        return None, None
    if not expectedCode(getCSID(message), csid):
        return None, None
    
    #Return Game ID and Role
    return getGID(message), getRole(message)


