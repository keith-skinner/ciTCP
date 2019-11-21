#!/usr/bin/env python3
import socket, logging, time
from citcp.header import Header
from citcp.state import TCPState
from citcp.tcb import Tcb


MSG_SIZE = 1024
PAYLOAD_SIZE = MSG_SIZE - Header.LENGTH
TIMED_WAIT = 100 / 1000


def rawSend(tcb, header, data=b''):
    logging.info(f"Sending:")
    logging.info(f"\tHeader: {header}")
    logging.info(f"\tData: {data}")
    tcb.sock.sendto(header+data, tcb.conn_addr)


def sendHeader(tcb, header):
    logging.info(f"Sending:")
    logging.info(f"{header}")
    header_raw = header.to_bytes('big')
    rawSend(tcb, header_raw)


def dataSend(tcb, header, data):
    logging.info(f"Sending:")
    logging.info(f"{header}")
    logging.info(f"{data}")
    header_raw = header.to_bytes('big')
    data_raw = header.to_bytes('big')
    rawSend(tcb, header_raw, data_raw)


def recv(tcb):
    logging.info("Waiting to receive connection")
    data, address = tcb.sock.recvfrom(MSG_SIZE)
    logging.info(f"Received Data: {data}")
    header, payload = Header.from_bytes(data[:Header.LENGTH], 'big'), data[Header.LENGTH:]
    logging.info(f"Received Header:\n{header}")
    logging.info(f"Received Payload:\n{payload}")
    return header, payload, address


def recvHeader(tcb, *flags, nbytes=1):
    f = 0
    for flag in flags:
        f |= flag.value
    
    while True:
        header, _, _ = recv(tcb)
        if not header.isCorrupted():
            if header.getFlag(Header.Flags.ALL.value) == f.value:
                tcb.recv += nbytes
                break


def recvData(tcb):
    header, payload, _ = recv(tcb)
    if not header.isCorrupted():
        if header.getSYN():
            tcb.recv += len(payload)
            return payload, False
        if header.getFIN():
            return b'', True
    return b'', False


def splitFile(filename, size):
    file = open(filename, "rb")
    message = file.read(size)
    while message != "":
        yield message
        message = file.read(size)
    file.close()


def sendFile(tcb, filename):
    closed = False
    messages = splitFile(filename, PAYLOAD_SIZE)
    for message in messages:
        tcb.addSent(len)
        syn_data = Header.from_tcb(tcb, Header.Flags.SYN.value)
        dataSend(tcb, syn_data, message)
        
        header, payload, address = recv(tcb)
        while header.isCorrupted() and not header.getSYN() and not header.getFIN():
            header, payload, address = recv(tcb)
        
        if header.getFIN():
            closed = True
    return closed


def FinSendAction(tcb):
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.FIN))


def FinWait1Action(tcb):
    recvHeader(Header.Flags.ACK)


def FinWait2Action(tcb):
    recvHeader(tcb, Header.Flags.FIN)
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.ACK))


def TimeWaitAction(tcb):
    time.sleep(TIMED_WAIT)


def FinReceivedAction(tcb):
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.ACK))


def CloseWaitAction(tcb):
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.FIN))


def LastAckAction(tcb):
    recvHeader(tcb, Header.Flags.ACK)


def SynReceivedAction(tcb):
    recvHeader(tcb, Header.Flags.ACK)


def ListenAction(tcb):
    recvHeader(tcb, Header.Flags.SYN)
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.SYN, Header.Flags.ACK))


def ClosedAction(tcb):
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.SYN))


def SynSentAction(tcb):
    recvHeader(tcb, Header.Flags.SYN)


def openResponderSequence(tcb, state):
    ListenAction(tcb)
    state.changeState(TCPState.SYN_RECIEVED)
    SynReceivedAction(tcb)
    state.changeState(TCPState.ESTABLISHED)
    return state


def openInitiatorSequence(tcb, state):
    ClosedAction(tcb)
    state.changeState(TCPState.SYN_SENT)
    SynSentAction(tcb)
    state.changeState(TCPState.ESTABLISHED)
    return state


def closeInitiatorSequence(tcb, state):
    FinSendAction(tcb)
    state.changeState(TCPState.FIN_WAIT_1)
    FinWait1Action(tcb)
    state.changeState(TCPState.FIN_WAIT_2)
    FinWait2Action(tcb)
    state.changeState(TCPState.TIME_WAIT)
    TimeWaitAction(tcb)
    state.changeState(TCPState.CLOSED)
    return state


def closeResponderSequence(tcb, state):
    FinReceivedAction(tcb)
    state.changeState(TCPState.CLOSE_WAIT)
    CloseWaitAction(tcb)
    state.changeState(TCPState.LAST_ACK)
    LastAckAction(tcb)
    state.changeState(TCPState.CLOSED)
    return state
