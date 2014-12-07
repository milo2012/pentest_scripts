"""
ScreenField object
Created by Kenneth J. Pouncey 2002-05-23
"""
import Screen5250

__all__ = ["SessionField"]

# Tunable parameters
DEBUGLEVEL = 0

class ScreenField:
    """Session Field interface class. """
    def __init__(self,screen):
        """Constructor. """
        self.debuglevel = DEBUGLEVEL
        self.screen = screen

    def set_debuglevel(self, debuglevel):
        """Set the debug level.
        The higher it is, the more debug output you get (on sys.stdout).
        """
        self.debuglevel = debuglevel

    def setField(self,attr,row,col,len,ffw1,ffw2,fcw1,fcw2):
        """ Set the field attributes """
        self.length = len
        self.startPos = (row * self.screen.getCols()) + col
        self.endPos = self.startPos + len -1
        self.cursorProg = 0
        self.fieldId = 0
        self.attr = attr
        self.setFFWs(ffw1,ffw2)
        self.setFCWs(fcw1,fcw2)
        self.next = None
        self.prev = None
        return self

    def getAttr(self):
        return self.attr

    def getHighlightedAttr(self):
        return self.fcw2 | 0x20

    def getLength(self):
        return self.length

    def setFFWs(self,ffw1,ffw2):
        self.ffw1 = ffw1;
        self.ffw2 = ffw2;
        self.mdt = (ffw1 & 0x8 ) == 0x8;
        return self.mdt;

    def setFCWs(self,fcw1,fcw2):
        self.fcw1 = fcw1;
        self.fcw2 = fcw2;
        if (fcw1 == 0x88):
            self.cursorProg = fcw2;

    def getFFW1(self):
        return self.ffw1

    def getFFW1(self):
        return self.ffw2

    def getFCW1(self):
        return self.ffc1

    def getFCW1(self):
        return self.ffc2

    def getFieldLength(self):
        return self.length

    def getFieldId(self):
        return self.fieldId

    def setFieldId(self,fi):
        self.fieldId = fi

    def getCursorProgression(self):
        return self.cursorProg

    def getCursorRow(self):
        return cursorPos / self.screen.getCols();

    def getCursorCol(self):
        return cursorPos % self.screen.getCols();

    def changePos(self,i):
        self.cursorPos += i

    def getText(self):
        start = self.startPos
        text = []
        while start <= self.endPos:
            text.append(self.screen.textPlane[start])
            start += 1
        return text

    def setString(self,text):
        start = self.startPos
        for x in text:
            self.screen.textPlane[start] = x
            start += 1
        self.mdt = 1
        self.screen.notify_screen_listeners(0)

    def setFieldChar(self,c):
        x = self.length
        self.cursorPos = self.startPos
        while x > 0:
            self.screen.textPlane[cursorPos] = c
            self.changePos(1)
            x -= 1

    def resetMDT(self):
        self.mdt = 0

    def setMDT(self):
        self.mdt = 1

    def isBypassField(self):
        return (self.ffw1 & 0x20) == 0x20

    def getAdjustment(self):
        return (self.ffw2 & 0x7)

    def isFER(self):
        return (self.ffw2 & 0x40) == 0x40

    def isMandatoryEnter(self):
        return (self.ffw2 & 0x8) == 0x8

    def isToUpper(self):
        return (self.ffw2 & 0x20) == 0x20

    def getFieldShift(self):
        """
            return bits 5 - 7 of FFW1 which holds the shift adjustment
            of the field
        """
        return (self.ffw1 & 0x7)

    def isHighlightedEntry(self):
        return (self.fcw1 == 0x89)

    def isAutoEnter(self):
        return (self.ffw2 & 0x80) == 0x80

    def isSignedNumeric(self):
        return (self.getFieldShift() == 7)

    def getKeyPosRC(self,row1,col1):
        x = ((row1 * self.screen.getCols()) + col1);
        y = x - self.startPos;
        self.cursorPos = x;
        return y;

    def getKeyPos(self, pos):
        y = self.pos - self.startPos
        self.cursorPos = pos
        return y

    def getCurrentPos(self):
        return self.cursorPos

    def withinField(self,pos):
        if (pos >= self.startPos) and (pos <= self.endPos):
            return 1
        return 0

    def startPos(self):
        return self.startPos

    def startRow(self):
        return self.startPos / self.screen.getCols()

    def startCol(self):
        return self.startPos % self.screen.getCols()

    def endPos(self):
        return self.endPos

    def toString(self):
        return 'startRow =', self.startRow(), 'startCol =',self.startCol(), \
               'length =',self.length,'ffw1 = ',self.ffw1,'ffw2 = ',self.ffw1, \
               'is bypass field',self.isBypassField(),'isAutoEnter', \
               self.isAutoEnter(),'is Mandatory Enter',self.isMandatoryEnter(), \
               'modified',self.mdt