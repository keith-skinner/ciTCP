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
    nBytes = tcb.sock.sendto(header+data, 0, tcb.conn_addr)
    logging.info(f"Sent:")
    logging.info(f"  Header: {header}")
    logging.info(f"  Data:   {data}")
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


def recvHeader(tcb, *flags, setaddr = False):
    f = Header.collectFlags(flags)
    while True:
        header, payload, address = recv(tcb)
        if header.isCorrupted(address, payload):
            # TODO: Ask for resend
            continue

        # if not header.correctSynAck(tcb):
            # TODO: Ask for resend
            # TODO: Ask if this is correct
            # continue

        elif header.getFlag(f):
            if setaddr:
                tcb.conn_addr = address
            return header
        # else drop packet by doing nothing with it


def recvData(tcb):
    while True:
        header, payload, address = recv(tcb)
        if header.isCorrupted(address, payload):
            #TODO: Ask for resend
            continue

        if header.getSYN():
            tcb.recv += len(payload)
            return payload, False

        if header.getFIN():
            return b'', True


def splitFile(file, chunk=PAYLOAD_SIZE):
    while True:
        value = file.read(chunk)
        if not value:
            break
        yield value


def sendFile(tcb, filename):
    with open(filename, 'rb') as file:
        for message in splitFile(file, PAYLOAD_SIZE):
            syn_data = Header.from_tcb(tcb, Header.Flags.SYN)
            dataSend(tcb, syn_data, message)
            tcb.sent += len(message)
            
            header = recvHeader(tcb, Header.Flags.ACK, Header.Flags.FIN)
            if header.getFIN():
                return True
    return False


def receiveFile(tcb, filename):
    with open(filename, 'wb') as file:
        closed = False
        while not closed:
            payload, closed = recvData(tcb)
            file.write(payload)
            if not closed:
                sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.ACK))


def FinSendAction(tcb):
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.FIN))


def FinWait1Action(tcb):
    recvHeader(tcb, Header.Flags.ACK)


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
    ack_header = recvHeader(tcb, Header.Flags.ACK)


def ListenAction(tcb):
    syn_header = recvHeader(tcb, Header.Flags.SYN, setaddr=True)
    tcb.ack = syn_header.seq
    tcb.recv += 1
    sendHeader(tcb, Header.from_tcb(tcb, Header.Flags.SYN, Header.Flags.ACK))
    tcb.sent += 1


def SynReceivedAction(tcb):
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
    tcb.ack = synack_header.seq
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
