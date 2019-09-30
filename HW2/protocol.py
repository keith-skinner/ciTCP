#!/usr/bin/env python3
import socket, logging
from common import recvall
import Message from message


def send(socket, message):
    socket.sendall(message)
    logging.info(f'Sent: {message}')


def recv(socket, length):
    message = recvall(socket, length).decode('utf-8')
    logging.info(f'Received: {message}')
    return message


def expectedSegment(message, expected):
    return expectedSegments(message, expected)


def expectedSegments(message, *argv):
    found = False
    for expected in argv:
        if message.startswith(expected):
            found = True
    if not found:
        logging.error(
            'Recieved bad message from server:\n' +
            '    Expected: ' + ' '.join(argv) + '\n' +
            '    Recieved: ' + message)
    return found


def rejected(message):
    if message.getCode().startswith(Message.Code.RJCT)
        logging.info('Rejected from server: '+ message)
        return True
    return False


def ClientRequestConnect(socket):
    logging.info('Requesting to connect')
    message = Message(Message.Code.CONN)
    send(socket, str(message))

    length = Message.length(
        Message.Segment.CODE, 
        Message.Segment.SID)
    message.set(recv(socket, length))

    if rejected(message):
        return None, 'Client was rejected from server'
    if not expectedSegment(message.getCode(), Message.Code.CONN):
        return None, 'Unexpected message from server'
    return message.getSID()


def ClientValidateSID(socket, sid):
    logging.info('Requesting sid validation')
    message = Message(Message.Code.CONF, sid)
    send(socket, str(message))

    length = Message.length(
        Message.Segment.CODE, 
        Message.Segment.SID)
    message.set(recv(socket, length))

    if rejected(message):
        return None, 'Client was rejected from server'
    if not expectedSegment(message.getCode(), Message.Code.CONF):
        return None, 'Incorrect sid, request new session id'
    if not expectedSegment(message.getSID(), sid):
        return None, 'Incorrect response from server'
    return sid, None


def ClientRequestGame(socket, sid):
    logging.info('Requesting to play')
    message = Message(Message.Code.CGID, sid)
    send(socket, str(message))
    
    length = Message.length(
        Message.Segment.CODE, 
        Message.Segment.SID)
    message.set(recv(socket, length))

    if rejected(message):
        return None, 'Rejected from server'
    if not expectedSegment(message.getCode(), Message.Code.CGID):
        return None, 'Incorrect response from server'
    if not expectedSegment(message.getSID(), sid):
        return None, 'Incorrect response from server'
    
    gid = message.getGID()
    
    length = createMessageLength(
        Message.Segment.CODE, 
        Message.Segment.CSID, 
        Message.Segment.CGID, 
        Message.Segment.ROLE)
    message.set(recv(socket, length))

    if rejected(message):
        return None, 'Rejected from server'
    if not expectedSegment(message.getCode(), Message.Code.CGID):
        return None, 'Incorrect response from server'
    if not expectedSegment(message.getSID(message), sid):
        return None, 'Incorrect response from server'
    if not expectedSegment(message.getGID(message), gid):
        return None, 'Incorrect response from server'
    
    #Return Game ID and Role
    return gid, getRole(message)


def ClientValidateGID(socket, sid, gid):
    logging.info('Requesting gid validation')
    message = Message(Message.Code.CONF, sid, gid)
    send(socket, str(message))

    length = Message.length(
        Message.Segment.CODE, 
        Message.Segment.SID,
        Message.Segment.GID)
    message.set(recv(socket, length))

    if rejected(message):
        return None, 'Client was rejected from server'
    if not expectedSegment(message.getCode(), Message.Code.CONF):
        return None, 'Incorrect sid, request new session id'
    if not expectedSegment(message.getSID(), sid):
        return None, 'Incorrect response from server'
    return sid, None


def ClientRequestMove(socket, sid, gid, position):
    logging.info('Requesting to make turn')
    message = Message(Message.Code.CMOV, csid, gid, position)
    send(socket, str(message))

    length = createMessageLength(CODE_LEN, CSID_LEN, GID_LEN)
    message = recv(socket, length)

    if rejected(message):
        return None, None
    if not expectedCodes(message, CONFIRM, REJECT):
        return None, None 
    if not expectedCode(getCSID(message), csid):
        return None, None
    if not expectedCode(getGID(message), gid):
        return None, None

    accepted = False
    if getCode(message) == TURN:
        accepted = True
    if getCode(message) == REJECT:
        accepted = False

    length = createMessage(CODE_LEN, CSID_LEN, GID_LEN)
    message = recv(socket, length)
    if rejected(message):
        return None, None
    if not expectedCodes(message, END_GAME, CONTINUE_GAME):
        return None, None
    if not expectedCode(getCSID(message), csid)
        return None, None
    if not expectedCode(getGID(message), gid)
        return None, None


def ClientSessionDisconnect(socket, sid):
    pass

def ClientGameDisconnect(socket, sid, gid):

