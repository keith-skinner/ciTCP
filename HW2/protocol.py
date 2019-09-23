#!/usr/bin/env python3
import socket, logging
from common import recvall

class Protocol:
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


    @staticmethod
    def getCode(message):
        return Protocol.splitMessage(message)[0]


    @staticmethod
    def getCSID(message):
        return Protocol.splitMessage(message)[1]
    

    @staticmethod
    def getGID(message):
        return Protocol.splitMessage(message)[2]

    @staticmethod
    def splitMessage(message):
        return message.split(':')

    @staticmethod
    def createMessage(*argv):
        return (':'.join(argv)).encode()


    @staticmethod
    def clientConnect(sock):
        toServer = Protocol.createMessage(Protocol.CONNECT)
        sock.sendall(toServer)
        logging.info(f'Sent: {toServer}')

        fromServer = recvall(sock, len(Protocol.CSID)+1+Protocol.SID_LEN).decode('utf-8')
        logging.info(f'Received: {fromServer}')
        
        code = Protocol.getCode(fromServer)         
        if code == Protocol.REJECT:
            logging.info('Rejected from server')
            return -1
        if code != Protocol.CSID:
            logging.info('Recieved bad message from server')
            return 0
        return Protocol.getCSID(fromServer)
        #TODO update pdf to not include redundent check on connection
    