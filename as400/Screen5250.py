"""
Screen object
Created by Kenneth J. Pouncey 2002-05-18
"""
import ScreenFields

__all__ = ["Screen5250"]

# Tunable parameters
DEBUGLEVEL = 0
# Initial Attribute
initAttr = 32

class Screen5250:
    #Screen5250 interface class.
    #def __init__(self, host=None, port=0):
    def __init__(self):         #Constructor
        self._listeners = []
        self.debuglevel = DEBUGLEVEL
        # Text Plane of screen
        self.textPlane = []
        # Attrubute Plane of screen
        self.attrPlane = []
        # number of rows and columns
        self.numRows = 24
        self.numCols = 80
        self.screenLength = self.numRows * self.numCols
        # current screen position
        self.lastPos = 0
        # current screen home position
        self.homePos = 0
        # pending insert flag
        self.pendingInsert = 0
        # screen virtual terminal
        self.vt = None
        # set default attribute for screen position row 1 column 1
        self.lastAttr = initAttr
        # set up our field format table
        self.screenFields = ScreenFields.ScreenFields(self)
        loop = 0
        while loop < self.screenLength:
            self.textPlane.append(' ')
            loop += 1
        loop = 0
        # initialize the attribute plane to default attribute of 0x32
        while loop < self.screenLength:
            self.attrPlane.append(self.lastAttr)
            loop += 1

    def set_debuglevel(self, debuglevel):
        """Set the debug level.
        The higher it is, the more debug output you get (on sys.stdout).
        """
        self.debuglevel = debuglevel

    def add_screen_listener( self , func ):
        # this is where we give it a "callback"
        self._listeners.append( func )

    def notify_screen_listeners( self, initiator ):
        """ this is where we actually call back """
        for f in self._listeners :
            f(initiator,1,1,24,80)

    def getRows(self):
        return self.numRows

    def getCols(self):
        return self.numCols

    def getCurrentRow(self):
        return (self.lastPos / self.numCols) + 1;

    def getCurrentCol(self):
      return (self.lastPos % self.numCols) + 1;

    def changePos(self,i):
        self.lastPos += i;
        if self.lastPos < 0:
            self.lastPos = self.screenLength + self.lastPos
        if self.lastPos > self.screenLength - 1:
            self.lastPos = self.lastPos - self.screenLength

    def moveTo(self,row,column):
        """
        This routine is based on offset 1,1 not 0,0 it will translate to
        offset 0,0 and call the goto_XY(int pos) it is mostly used from
        external classes that use the 1,1 offset
        """
        self.moveToPos(((row - 1) * self.numCols) + (column-1))

    def moveToPos(self,pos):
        self.lastPos = pos

    def addField(self,attr,fLength,ffw0,ffw1,fcw1,fcw2):
        self.lastAttr = attr
        self.textPlane[self.lastPos] = 0
        self.attrPlane[self.lastPos] = attr
        self.changePos(1)
        pos = self.lastPos
        sf = self.screenFields.setField(attr,self.getCurrentRow(), \
            self.getCurrentCol(),fLength,ffw0,ffw1,fcw1,fcw2)
        #print sf.toString()
        # now lets initialize the planes for the field
        while fLength > 0:
            if self.textPlane[pos] == 0:
                self.textPlane[pos] = ' '
                self.attrPlane[pos] = attr
            else:
                self.attrPlane[pos] = attr
            pos +=1
            fLength -=1
        spos = self.lastPos
        self.lastPos = pos
        self.setAttr(initAttr)
        self.lastAttr = attr
        self.lastPos = spos

    def setAttr(self,attr):
        """
        This routine is used to set attributes in the Attribute Plane
        """
        # print chr(char), ' at ' , self.getCurrentRow(),
        # ' , ' , self.getCurrentCol()
        self.lastAttr = attr
        self.attrPlane[self.lastPos] = attr
        self.changePos(1)
        pos = self.lastPos
        while pos < self.screenLength and self.attrPlane[pos] != \
              self.lastAttr:
            self.attrPlane[pos] = self.lastAttr
            pos += 1

    def setChar(self,char):
        """
        This routine is used to place characters into the Text Plane
        """
        if char > 0x0 and char < ' ':
            self.textPlane[self.lastPos] = ' '
            self.attrPlane[self.lastPos] = 33
        else:
            self.textPlane[self.lastPos] = char
        self.changePos(1)

    def clearAll(self):
        self.lastPos = 0
        self.lastAttr = 0x32
        self.clearFFT()
        self.clearPlanes()

    def clearFFT(self):
        self.screenFields.clearFFT()
        self.pendingInsert = 0
        self.homePos = -1

    def clearPlanes(self):
        x = 0
        # clear Text Plane
        while x < self.screenLength:
            self.textPlane[x] = ' '
            x += 1
        x = 0
        # clear Attribute Plane
        while x < self.screenLength:
            self.attrPlane[x] = self.lastAttr
            x += 1

    def getFields(self):
        """
            return an object of Fields contained on the presentation space.            
        """
        return self.screenFields

    def getPlaneData(self,row,column,endRow,endCol,whichPlane):
        loop = 0
        start = ((row - 1) * self.numCols) + (column-1)
        end = ((endRow - 1) * self.numCols) + (endCol-1)
        length = end - start
        if whichPlane == 1:     # Text Plane
            plane = ''
            indices = range(start,start + length)
            for idx in indices:
                c = self.textPlane[idx]
                if c < ' ':
                    plane += ' '
                else:
                    plane += c
            return plane
        elif whichPlane == 2:   # Attribute Plane
            return self.attrPlane[start:start + length]

    def setVT(self,vt):
        """ Set the virtual terminal associated with the screen """
        self.vt = vt

    def sendAidKey(self,aid):
        """ Send the aid key to the virtual terminal """
        self.vt.sendAidKey(aid)

    def getPos(self,row,col):
        """ Return a position integer from a passed row and column """
        return (row * self.numCols) + col

    def getRow(self,pos):
        """ Return row associated to a position """
        row = pos / self.numCols
        if row < 0:
            row =  self.lastPos / self.numCols
        if row > (self.screenLength - 1):
            row = self.screenLength - 1
        return row;

    def getCol(self,pos):
        """ Return col associated to a position """
        col = pos % self.numCols
        if col > 0:
            return col
        else:
            return 0

    def gotoFieldItem(self,item):
        """ Move the screen cursor position to the field item """
        sizeFields = self.screenFields.getCount()
        if item > sizeFields or item < 0:
            return 0
        self.screenFields.setCurrentField(self.screenFields.getItem(item-1))
        while self.screenFields.isCurrentFieldBypassField() and item < sizeFields:
            self.screenFields.setCurrentField(self.screenFields.getItem(item))
            item += 1
        return self.gotoField(self.screenFields.getCurrentField())

    def gotoField(self,f):
        if f != None:
            self.moveToPos(f.startPos)
            return 1
        else:
            return 0

    def setPendingInsert(self, flag, icX, icY):
        self.pendingInsert = flag
        if self.pendingInsert:
            self.homePos = self.getPos(icX,icY)

    def goHome(self):
        """
          now we try to move to first input field according to
          14.6 WRITE TO DISPLAY Command
            - If the WTD command is valid, after the command is processed,
                  the cursor moves to one of three locations:
            - The location set by an insert cursor order (unless control
                  character byte 1, bit 1 is equal to B'1'.)
            - The start of the first non-bypass input field defined in the
                  format table
            - A default starting address of row 1 column 1.
        """
        if self.pendingInsert:
            self.moveTo(self.getRow(self.homePos),self.getCol(self.homePos))
            self.isInField()   ## we now check if we are in a field
        else:
            if not self.gotoFieldItem(1):
                self.homePos = self.getPos(1,1);
                self.moveTo(1,1);
                self.isInField(row=0,col=0);   ## we now check if we are in a field
            else:
                self.homePos = self.getPos(self.getCurrentRow(),self.getCurrentCol())

    def isInField(self,pos=None,row=None,col=None,chgToField=None):
        if chgToField == None:
            chgToField = 1
        else:
            chgToField = 0
        if row != None:
            pos = (row * self.numCols) + col
        if pos == None:
            pos = self.lastPos
        return self.screenFields.isInField(pos,chgToField)
