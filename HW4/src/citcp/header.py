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
        FIN = 0b001

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
            self.flags
        )

    @classmethod
    def create(cls, seq, ack, window, flags):
        temp = cls(seq, ack, window, 0, flags)
        temp.setChecksum(cls.calcChecksum())
        return temp

    def resetFlags(self):
        self.flags = 0
        return self

    def setACK(self):
        self.flags |= Flags.ACK.value
        return self
    
    def setSYN(self):
        self.flags |= Flags.SYN.value
        return self
    
    def setFIN(self):
        self.flags |= Flags.FIN.value
        return self

    def getFlag(self, mask):
        return 1 if self.flags & mask != 0 else 0

    def getACK(self):
        return self.getFlag(Flags.ACK.value)

    def getSYN(self):
        return self.getFlag(Flags.SYN.value)
    
    def getFIN(self):
        return self.getFlag(Flags.FIN.value)
    
    def setSeqNum(self, number):
        if number < 0 or number >= Limits.MAX_SEQ.value:
            raise ValueError("number ({}) must be in [0, 2**16)".format(number))
        self.seq = number
        return self
    
    def setAckNum(self, number):
        if number < 0 or number >= Limits.MAX_ACK.value:
            raise ValueError("number ({}) must be in [0, 2**16)".format(number))
        self.ack = number
        return self
    
    def setWindow(self, window):
        if window < 0 or window >= Limits.MAX_WINDOW:
            raise ValueError("window ({}) must be in [0, 2**16)".format(window))
        self.window = window
        return self

    def setChecksum(self, checksum):
        if checksum < 0 or checksum >= Limits.MAX_CHECKSUM:
            raise ValueError("checksum ({}) must be in [0, 2**16)".format(checksum))
        self.checksum = checksum
        return self

    def calcChecksum(self):
        #TODO: Create calculation
        return 0

    def isCorrupted(self):
        return self.calcChecksum() != self.checksum

    def toBytes(self, order):
        b = self.seq.to_bytes(2, order)
        b += self.ack.to_bytes(2, order)
        b += self.window.to_bytes(2, order)
        b += self.checksum.to_bytes(2, order)
        b += self.flags.to_bytes(1, order)
        return b
    
    @classmethod
    def fromBytes(cls, bytes, order):
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
        U = 'unused' if self.flags & ~0b111 == 0 else str(self.flags & ~0b111)
        s  = '\n\t|0                            15|16                           31| bit'
        s += '\n\t+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'
        s += '\n\t|{:^31}|{:^31}|'.format(self.seq, self.ack)
        s += '\n\t+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'
        s += '\n\t|{:^31}|{:^31}|'.format(self.window, self.checksum)
        s += '\n\t+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'
        s += '\n\t|{:^9}|{}|{}|{}|'.format(U, A, S, F)
        s += '\n\t+-+-+-+-+-+-+-+-+'
        return s

    @classmethod
    def length(cls):
        #number of bytes
        return 9

    def __len__(self):
        return Header.length()