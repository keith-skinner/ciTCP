#!/usr/bin/env python3
import socket, logging, time
from citcp.header import Header
from citcp.state import TCPState
from citcp.tcb import Tcb

# Total message size
MSG_SIZE = 1024
# Size of payload from message
PAYLOAD_SIZE = MSG_SIZE - Header.LENGTH
# How long to wait until the package is considered lost
TIMEOUT_WAIT_DEFAULT = 200 / 1000
# How long to wait until socket can reset
TIMED_WAIT = 100 / 1000


def rawSend(tcb, header, data=b''):
    nBytes = tcb.sock.sendto(header+data, tcb.conn_addr)
    logging.info(f"Sent:")
    logging.info(f"\tHeader: {header}")
    logging.info(f"\tData: {data}")
    return nBytes


def sendHeader(tcb, header):
    logging.info("Sending:")
    logging.info(header)
    header_raw = header.to_bytes()
    return rawSend(tcb, header_raw)


def dataSend(tcb, header, data):
    logging.info("Sending:")
    logging.info(header)
    logging.info(data)
    header_raw = header.to_bytes()
    data_raw = header.to_bytes()
    return rawSend(tcb, header_raw, data_raw)

def rawRecv(tcb):
    logging.info("Receiving:")
    data, address = tcb.sock.recvfrom(MSG_SIZE)
    logging.info(f"Address: {address}")
    logging.info(f"Data: {data}")
    return data, address


def recv(tcb):
    data, address = rawRecv(tcb)
    header, payload = Header.from_bytes(data[:Header.LENGTH]), data[Header.LENGTH:]
    logging.info("Received")
    logging.info(header)
    logging.info(payload)
    return header, payload, address


def recvHeader(tcb, *flags, b=0):
    f = Header.collectFlags(flags)
    while True:
        header, _, _ = recv(tcb)
        if header.isCorrupted():
            #TODO: Ask for resend
            continue

        elif header.getFlag(f):
            tcb.recv += b
            return header
        # else drop packet by doing nothing with it


def recvData(tcb):
    while True:
        header, payload, _ = recv(tcb)
        if header.isCorrupted():
            #TODO: Ask for resend
            continue

        if header.getSYN():
            tcb.recv += len(payload)
            return payload, False

        if header.getFIN():
            return b'', True


def splitFile(filename, size, stop=False):
    with open(filename, "rb") as file:
        message = file.read(size)
        while not stop and message != "":
            yield message
            #Allows for early termination and closing of file
            if stop:
                return
            message = file.read(size)


def sendFile(tcb, filename):
    closed = False
    for message in splitFile(filename, PAYLOAD_SIZE):
        syn_data = Header.from_tcb(tcb, Header.Flags.SYN.value)
        dataSend(tcb, syn_data, message)
        
        header = recvHeader(tcb, Header.Flags.SYN, Header.Flags.FIN)
        if header.getFIN():
            closed = True
            break
    return closed

def receiveFile(tcb, filename):
    with open(filename, 'wb') as file:
        closed = False
        while not closed:
            payload, closed = recvData(tcb)
            file.write(payload)
            if not closed:
                sendHeader(tcb, Header.from_tcb(tcb, Header.FLags.ACK.value))


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
    h = recvHeader(tcb, Header.Flags.ACK)
    tcb.setAck(header.syn)
    if not h.getSYN():
        pass #TODO: what do i do here again?


def ListenAction(tcb):
    syn_header = recvHeader(tcb, Header.Flags.SYN)
    tcb.ack = header.syn
    tcb.recv += 1
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.SYN, Header.Flags.ACK))
    tcb.sent += 1


def SynReceivedAction(tcb):
    ack_header = recvHeader(tcb, Header.Flags.ACK)
    while ack_header.ack != tcb.seq+tcb.sent or ack_header.seq != tcb.ack+tcb.recv:
        #TODO: Ask for resend?
        ack_header = recvHeader(tcb, Header.Flags.ACK)


def openResponderSequence(tcb, state):
    ListenAction(tcb)
    state.changeState(TCPState.SYN_RECIEVED)
    SynReceivedAction(tcb)
    state.changeState(TCPState.ESTABLISHED)
    return state


def ClosedAction(tcb):
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.SYN))
    tcb.sent += 1


def SynSentAction(tcb):
    synack_header = recvHeader(tcb, Header.Flags.SYNACK)
    tcb.ack = synack_header.syn
    tcb.recv += 1
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.ACK))


def openInitiatorSequence(tcb, state):
    if state is None:
        state = TCPState.startingState()
    else:
        state.changeState(TCPState.CLOSED)
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
