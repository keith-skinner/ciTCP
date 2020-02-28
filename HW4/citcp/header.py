#!/usr/bin/env python
import sys
from enum import Enum

class Header:


    class Limits(Enum):
        MAX_SEQ = 2**16
        MAX_ACK = 2**16
        MAX_WINDOW = 2**16
        MAX_CHECKSUM = 2**16


    class Flags(Enum):
        ACK = 0b100
        SYN = 0b010
        SYNACK = 0b110
        FIN = 0b001
        ALL = 0b111


    # Number of bytes for header
    LENGTH = 9


    def __init__(self, seq=0, ack=0, window=0, checksum=0, flags=0):
        self.seq = seq
        self.ack = ack
        self.window = window
        self.checksum = checksum
        self.flags = flags


    def copy(self):
        return Header(
            self.seq, 
            self.ack, 
            self.window, 
            self.checksum,
            self.flags)


    @classmethod
    def from_tcb(cls, tcb, *flags):
        f = Header.collectFlags(flags)
        return cls(
            (tcb.seq+tcb.sent) % Header.Limits.MAX_SEQ.value, 
            (tcb.ack+tcb.recv) % Header.Limits.MAX_ACK.value, 
            (tcb.wind)         % Header.Limits.MAX_WINDOW.value, 
            0, 
            f
        )


    @staticmethod
    def collectFlags(flags):
        value=0
        for flag in flags:
            value |= flag.value
        return value


    def resetFlags(self):
        self.flags = 0
        return self


    def setACK(self):
        self.flags |= Header.Flags.ACK.value
        return self
    

    def setSYN(self):
        self.flags |= Header.Flags.SYN.value
        return self
    

    def setFIN(self):
        self.flags |= Header.Flags.FIN.value
        return self


    def getFlag(self, mask):
        return 1 if self.flags & mask != 0 else 0


    def getACK(self):
        return self.getFlag(Header.Flags.ACK.value)


    def getSYN(self):
        return self.getFlag(Header.Flags.SYN.value)
    

    def getFIN(self):
        return self.getFlag(Header.Flags.FIN.value)
    

    def setSeqNum(self, number):
        if number in range(0, Header.Limits.MAX_SEQ.value):
            raise ValueError("number ({number}) must be in [0, {Header.Limits.MAX_SEQ.value})".format(number))
        self.seq = number
        return self
    

    def setAckNum(self, number):
        if number in range(0, Header.Limits.MAX_ACK.value):
            raise ValueError("number ({number}) must be in [0, {Header.Limits.MAX_ACK.value})".format(number))
        self.ack = number
        return self
    

    def setWindow(self, window):
        if window in range(0, Header.Limits.MAX_WINDOW.value):
            raise ValueError("window ({window}) must be in [0, {Header.Limits.MAX_WINDOW.value})".format(window))
        self.window = window
        return self


    def setChecksum(self, checksum):
        if checksum in range(0, Header.Limits.MAX_CHECKSUM.value):
            raise ValueError("checksum ({checksum}) must be in [0, {Header.Limits.MAX_CHECKSUM.value})".format(checksum))
        self.checksum = checksum
        return self


    def addressToInt(self, address):
        pass 


    def calcChecksum(self, address, data=b''):
        #TODO: Create calculation
        
        return 0


    def isCorrupted(self, address, data=b''):
        return self.calcChecksum(address, data) != self.checksum


    def correctSynAck(self, tcb):
        return self.seq == tcb.ack+tcb.recv and self.ack == tcb.seq+tcb.sent

    def to_bytes(self, order=sys.byteorder):
        b  = self.seq.to_bytes(2, order)
        b += self.ack.to_bytes(2, order)
        b += self.window.to_bytes(2, order)
        b += self.checksum.to_bytes(2, order)
        b += self.flags.to_bytes(1, order)
        return b
    

    @classmethod
    def from_bytes(cls, bytes, order=sys.byteorder):
        seq = int.from_bytes(bytes[0:2], order)
        ack = int.from_bytes(bytes[2:4], order)
        window = int.from_bytes(bytes[4:6], order)
        checksum = int.from_bytes(bytes[6:8], order)
        flags = int.from_bytes(bytes[8:9], order)
        return cls(seq, ack, window, checksum, flags)


    def __str__(self):
        A = 'A' if self.getACK() else ' '
        S = 'S' if self.getSYN() else ' '
        F = 'F' if self.getFIN() else ' '
        U = self.flags & ~Header.Flags.ALL.value
        U = 'unused' if U == 0 else str(U)
        s  = '\n\t|0                            15|16                           31| bit'
        s += '\n\t+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'
        s += '\n\t|{:^31}|{:^31}|'.format(self.seq, self.ack)
        s += '\n\t+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'
        s += '\n\t|{:^31}|{:^31}|'.format(self.window, self.checksum)
        s += '\n\t+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'
        s += '\n\t|{:^9}|{}|{}|{}|'.format(U, A, S, F)
        s += '\n\t+-+-+-+-+-+-+-+-+'
        return s


    def __len__(self):
        return Header.LENGTH