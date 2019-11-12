#!/usr/bin/env python

import sys

class Header:
    def __init__(self, seq=0, ack=0, window=0, checksum=0, flags=0):
        self.seq = seq
        self.ack = ack
        self.window = window 
        self.checksum = checksum
        self.flags = flags

    def copy(self):
        h = Header(
            self.seq, 
            self.ack, 
            self.window, 
            self.checksum,
            self.flags
        )
        return h

    def resetFlags(self):
        self.flags = 0
        return self

    def setACK(self):
        self.flags |= 0b100
        return self
    
    def setSYN(self):
        self.flags |= 0b010
        return self
    
    def setFIN(self):
        self.flags |= 0b001
        return self

    def getFlag(self, mask):
        return 1 if self.flags & mask != 0 else 0

    def getACK(self):
        return self.getFlag(0b100)

    def getSYN(self):
        return self.getFlag(0b010)
    
    def getFIN(self):
        return self.getFlag(0b001)
    

    def setSeqNum(self, number):
        if number < 0 or number >= 2**16:
            raise ValueError("number ({}) must be in [0, 2**16)".format(number))
        self.seq = number
        return self
    
    def setAckNum(self, number):
        if number < 0 or number >= 2**16:
            raise ValueError("number ({}) must be in [0, 2**16)".format(number))
        self.ack = number
        return self
    
    def setWindow(self, window):
        if window < 0 or window >= 2**16:
            raise ValueError("window ({}) must be in [0, 2**16)".format(window))
        self.window = window
        return self

    def setChecksum(self, checksum):
        if checksum < 0 or checksum >= 2**16:
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
        s  = '|0                            15|16                           31| bit\n'
        s += '+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n'
        s += '|{:^31}|{:^31}|\n'.format(self.seq, self.ack)
        s += '+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n'
        s += '|{:^31}|{:^31}|\n'.format(self.window, self.checksum)
        s += '+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n'
        s += '|{:^9}|{}|{}|{}|\n'.format(U, A, S, F)
        s += '+-+-+-+-+-+-+-+-+'
        return s

    @staticmethod
    def length(self):
        #number of bytes
        return 9

    def __len__(self):
        return Header.length()