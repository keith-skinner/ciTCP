import Enum from enum

class Message:

    class Code(Enum):
        CONN = 'CONN'
        DCON = 'DCON'
        RJCT = 'RJCT'
        CONF = 'CONF'
        ENDG = 'ENDG'
        CONT = 'CONT'
        TURN = 'TURN'
        PLAY = 'PLAY'
        CSID = 'CSID'

    #Lengths of each segment
    class Segment(Enum):
        CODE = 4
        SID = 4
        GID = 4
        ROLE = 1

    def __init__(self, message):
        self.set(message)

    def set(self, message):
        self.message = message.split(':')
    
    def join(self):
        return (':'.join(self.message)).encode()

    def getCode(self):
        return self.message[0]

    def getSID(self):
        return self.message[1]

    def getGID(self):
        return self.message[2]

    def getRole(self):
        return self.message[3]

    @staticmethod
    def create(*args):
        return (':'.join(args)).encode()
    
    @staticmethod
    def length(*args):
        #Args is not actual message content, but the lengths of segments
        #  The len(args)-1 accounts for the ':'s
        return sum(args) + len(args)-1

    def __str__(self):
        return self.join()
