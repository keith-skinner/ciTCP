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


def ClientPlayRequest(socket, sid):
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
    
    return message.getGID(), None


def ClientRoleAssignment(socket, sid, gid):
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
    
    return message.getRole(message), None
    

def ClientRequestGame(socket, sid):
    logging.info('Requesting to play')
    gid, reason = ClientPlayRequest(socket, sid)
    if gid is None:
        return None, None, reason
    
    role, reason = ClientRoleAssignment(socket, sid, gid)
    if role is None:
        return None, None, reason

    return gid, role, None


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


def ClientReceiveMove(socket, sid, gid, position):
    logging.info('Receiving Opponent\'s Move')
    length = Message.length(
        Message.Segment.CODE,
        Message.Segment.CSID,
        Message.Segment.CGID,
        Message.Segment.MOVE)
    message = Message().set(recv(socket, length))
    
    if rejected(message):
        return None, 'Client was rejected from server'
    if not expectedSegment(message.getCode(), Message.Segment.CMOV)
        return None, 'Unexpected message from server'
    if not expectedSegment(message.getSID(), sid)
        return None, 'Unexpected message from server'
    if not expectedSegment(message.getGID(), gid)
        return None, 'Unexpected message from server'
    
    return message.getMove()


def ClientRequestMove(socket, sid, gid, position):
    logging.info('Requesting to make turn')
    message = Message(Message.Code.CMOV, sid, gid, position)
    send(socket, str(message))

    length = Message.length(
        Message.Segment.CODE,
        Message.Segment.CSID, 
        Message.Segment.CGID,
        Message.Segment.MOVE)
    message = message.set(recv(socket, length))

    if rejected(message):
        return None, 'Client was rejected from server'
    if not expectedSegments(message, Message.Code.CONF, Message.Code.DENY):
        return None, 'Unexpected message from server'
    if not expectedSegment(message.getSID(), sid):
        return None, 'Unexpected message from server'
    if not expectedCode(message.getGID(), gid):
        return None, 'Unexpected message from server'
    if message.getCode() == Message.Code.Deny:
        return False, f'Position already taken: {position}'
    return True, None


def ClientGameOver(socket, sid, gid):
    length = createMessage(
        Message.Code.CODE,
        Message.Code.SID, 
        Message.Code.GID)
    message = Message().set(recv(socket, length))

    if rejected(message):
        return None, 'Client was rejected from server'
    if not expectedSegments(message, END_GAME, CONTINUE_GAME):
        return None, 'Unexpected message from server'
    if not expectedSegments(message.getSID(), sid)
        return None, 'Unexpected message from server'
    if not expectedSegments(message.getGID(), gid)
        return None, 'Unexpected message from server'
    
    if message.getCode() == Message.Code.ENDG:
        return True, None
    if message.getCode() == Message.Code.CONT:
        return False, None
    return None, 'Unexpected message from server'


def ClientSessionDisconnect(socket, sid):
    message = Message(Message.Code.DCON, sid)
    send(socket, str(message))


def ClientGameDisconnect(socket, sid, gid):
    message = Message(Message.Code.ENDG, sid, gid)
    send(socket, str(message))

