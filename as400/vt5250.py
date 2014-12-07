"""Enhanced Telnet 5250 client class.
Based on RFC 1205: 5250 Telnet Protocol Specification, by P. Chmielewski
Example:
>>>from tnvtlib import Telnet5250 tn = Telnet5250('www.net400.org', 23)
>>>connect to as400 host
Created by Kenneth J. Pouncey 2002-05-10
"""

# Import modules
import sys
import socket
import select
import Queue
import CodePage
import Screen5250

__all__ = ["vt5250"]

# Tunable parameters
DEBUGLEVEL = 0

# buffersize
BUFSIZE = 8*1024

# Telnet protocol defaults
TELNET_PORT = 23

# Telnet protocol characters (don't change)
IAC  = chr(255) # "Interpret As Command"
DONT = chr(254)
DO   = chr(253)
WONT = chr(252)
WILL = chr(251)
theNULL = chr(0)
SB = chr(250)     # begin subnegotiation
SE = chr(240)     # end subnegotiation
QUAL_IS = chr(0)  # qualifier is
EOR = chr(239)    # End of record
TERMINAL_TYPE = chr(24)       # terminal type
OPT_END_OF_RECORD = chr(25)   # End of record option RFC 885
TRANSMIT_BINARY = chr(0)      # transmit binary RFC 856
TIMING_MARK = chr(6)          # not used yet
NEW_ENVIRONMENT = chr(39)     # not used yet

class vt5250:
    """vt5250 interface class.
    An instance of this class represents a connection to a telnet server.
    The instance is initially not connected; the open() method must be
    used to establish a connection.  Alternatively, the host name and
    optional port number can be passed to the constructor, too.
    Don't try to reopen an already connected instance.
    This class has many read_*() methods.  Note that some of them raise
    EOFError when the end of the connection is read, because they can
    return an empty string for other reasons.
    See the individual doc strings.
    read_all()
        Read all data until EOF; may block.
    read_some()
        Read at least one byte or EOF; may block.
    """

    def __init__(self, host=None, port=0):
        """Constructor.
        When called without arguments, create an unconnected instance.
        With a hostname argument, it connects the instance; a port
        number is optional.
        """
        self.debuglevel = DEBUGLEVEL
        self.host = host
        self.port = port
        self.sock = None
        self.rawq = ''
        self.irawq = 0
        self.cookedq = ''
        self.eof = 0
        self.buffer = ''
        self.saveStream = ''
        self.readType = 0
        self.codePage = CodePage.CodePage()

        # Create the queue
        self.queue = Queue.Queue()

        if host:
            self.open(host, port)

    def open(self, host, port=0):
        """Connect to a host.
        The optional second argument is the port number, which
        defaults to the standard telnet port (23).
        Don't try to reopen an already connected instance.
        """
        self.eof = 0
        if not port:
            port = TELNET_PORT
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.interact()

    def __del__(self):
        """Destructor -- close the connection."""
        self.close()

    def msg(self, msg, *args):
        """Print a debug message, when the debug level is > 0.
        If extra arguments are present, they are substituted in the
        message using the standard string formatting operator.
        """
        if self.debuglevel > 0:
            print 'Telnet5250(%s,%d):' % (self.host, self.port),
            #if args:
            #    print msg % args
            #else:
            #    print msg

    def set_debuglevel(self, debuglevel):
        """Set the debug level.
        The higher it is, the more debug output you get (on sys.stdout).
        """
        self.debuglevel = debuglevel

    def close(self):
        """Close the connection."""
        if self.sock:
            self.sock.close()
        self.msg("socket closing down")
        self.sock = 0
        self.eof = 1
        self.running = 0
        self.queue.put(None)
        self.msg("socket closed down")

    def get_socket(self):
        """Return the socket object used internally."""
        return self.sock

    def fileno(self):
        """Return the fileno() of the socket object used internally."""
        return self.sock.fileno()

    def write(self, buffer):
        """Write a string to the socket, doubling any IAC characters.
        Can block if the connection is blocked.  May raise
        socket.error if the connection is closed.
        """
        if IAC in buffer:
            buffer = buffer.replace(IAC, IAC+IAC)
        self.msg("send %s", `buffer`)
        self.sock.send(buffer)

    def writeGDS(self,flags, opcode, bytes):
        """Write a string to the socket, doubling any IAC characters.
        Can block if the connection is blocked.  May raise
        socket.error if the connection is closed.
        """
        length = 10
        buffer = []
        if len(bytes) > 0:
           if IAC in bytes:
              bytes = bytes.replace(IAC, IAC+IAC)
           length = len(bytes) + 10
        buffer = chr(length >> 8)
        buffer += chr(length & 0xff)
        buffer += chr(0x12)
        buffer += chr(0xA0)
        buffer += chr(0x0)
        buffer += chr(0x0)
        buffer += chr(0x04)
        buffer += chr(flags)
        buffer += chr(0x0)
        buffer += chr(opcode)
        for x in bytes:
            buffer += chr(x)
            #buffer += bytes
        buffer += IAC
        buffer += EOR
        self.msg("send %s", `buffer`)
        self.sock.send(buffer)
        #self.sock.flush()

    def read_all(self):
        """Read all data until EOF; block until connection closed."""
        self.process_rawq()
        while not self.eof:
            self.load_stream()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = ''
        return buf

    def read_incoming(self):
        """Read all data until EOF; block until connection closed."""
        #print 'reading'
        self.process_rawq()
        while not self.eof:
            self.readIncoming()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = ''
        return buf

    def process_rawq(self):
        """
        Transfer from raw queue to cooked queue.
        Set self.eof when connection is closed.
        Don't block unless in the midst of an IAC sequence.
        """
        buf = ''
        try:
            while self.rawq:
                c = self.rawq_getchar()
                buf = buf + c
        except EOFError: # raised by self.rawq_getchar()
            pass
        self.cookedq = self.cookedq + buf

    def rawq_getchar(self):
        """
        Get next char from raw queue.
        Block if no data is immediately available.
        Raise EOFError when connection is closed.
        """
        if not self.rawq:
            self.fill_rawq()
            if self.eof:
                raise EOFError
        c = self.rawq[self.irawq]
        self.irawq = self.irawq + 1
        if self.irawq >= len(self.rawq):
            self.rawq = ''
            self.irawq = 0
        return c

    def fill_rawq(self):
        """Fill raw queue from exactly one recv() system call.
        Block if no data is immediately available.
        Set self.eof when connection is closed.
        """
        if self.irawq >= len(self.rawq):
            self.rawq = ''
            self.irawq = 0
        buf = self.sock.recv(BUFSIZE)
        self.msg("recv %s", `buf`)
        self.eof = (not buf)
        self.rawq = self.rawq + buf

    def loadStream(self,stream):
        """
        Fill raw queue from exactly one recv() system call.
        Block if no data is immediately available.
        Set self.eof when connection is closed.
        """
        j = 0
        size = 0
        self.msg("recv from load stream %s", `stream`)
        if self.saveStream == '':
            j = (ord(stream[0]) & 0xff) << 8 | (ord(stream[1]) & 0xff);
            size = len(stream);
        else:
            size = len(self.saveStream) + len(stream)
            stream = self.saveStream + stream
            j = (ord(stream[0]) & 0xff) << 8 | (ord(stream[1]) & 0xff);
            self.saveStream = ''
        if j > size:
            self.saveStrem = stream
        else:
            self.queue.put(stream)
        #here
	#print j,size,len(stream)
        #self.msg("recv from load stream %s", `stream`)

    def readIncoming(self):
        """
        Fill raw queue from exactly one recv() system call.
        Block if no data is immediately available.
        Set self.eof when connection is closed.
        """
        if self.irawq >= len(self.rawq):
            self.rawq = ''
            self.irawq = 0
        buf = self.sock.recv(BUFSIZE)
        self.buffer = self.buffer + buf
        self.msg("recv readIncoming %s" % `self.buffer`)
        buffer = ''
        j = -1
        startOffset = 0
        indices = range(len(self.buffer))
        for idx in indices :
            i = self.buffer[idx]
            if (j == IAC) and (i == IAC):
                j = -1
                continue
            else:
                buffer = buffer + i
                if (j == IAC) and (i == EOR):
                    self.loadStream(buffer[startOffset:idx])
                    startOffset = idx + 1
                    #self.eof = (not buffer)
                    #buffer = ''
                j = i
        if startOffset < idx:
            self.loadStream(buffer[startOffset:idx])
	#here1
        #print idx,startOffset,len(self.buffer)
        self.buffer = ''

    def sock_avail(self):
        """Test whether data is available on the socket."""
        return select.select([self], [], [], 0) == ([self], [], [])

    def process_negotiations(self):
        """
        Transfer from raw queue to cooked queue.
        Set self.eof when connection is closed.
        Don't block unless in the midst of an IAC sequence.
        """
        buf = ''
        done = 0
        try:
           c = self.rawq_getchar()
           while c == IAC:
                c = self.rawq_getchar()
                if c == IAC:
                    buf = buf + c
                elif c == DO:
                    opt = self.rawq_getchar()
                    if opt == NEW_ENVIRONMENT:
                        self.msg('IAC DO NEW_ENVIRONMENT')
                        self.msg('sending : IAC WONT NEW_ENVIRONMENT')
                        self.sock.send(IAC + WONT + NEW_ENVIRONMENT)
                    elif opt == TERMINAL_TYPE:
                        self.msg('IAC DO TERMINAL_TYPE')
                        self.msg('sending : IAC WILL TERMINAL_TYPE')
                        self.sock.send(IAC + WILL + TERMINAL_TYPE)
                    elif opt == OPT_END_OF_RECORD:
                        self.msg('IAC DO OPT_END_OF_RECORD')
                        self.msg('sending : IAC WILL OPT_END_OF_RECORD')
                        self.sock.send(IAC + WILL + OPT_END_OF_RECORD)
                    elif opt == TRANSMIT_BINARY:
                        self.msg('IAC DO TRANSMIT_BINARY')
                        self.msg('sending: IAC WILL TRANSMIT_BINARY')
                        self.sock.send(IAC + WILL + TRANSMIT_BINARY)
                    else:
                        # default that we wont
                        self.msg('IAC DO %d', ord(opt))
                        self.msg('sending : IAC WONT %d', ord(opt))
                        self.sock.send(IAC + WONT + opt)
                elif c == DONT:
                    opt = self.rawq_getchar()
                    self.msg('IAC %s %d', c == DO and 'DO' or 'DONT', \
                             ord(c))
                    self.sock.send(IAC + WONT + opt)
                elif c == WILL:
                    opt = self.rawq_getchar()
                    if opt == OPT_END_OF_RECORD:
                        self.msg('IAC WILL OPT_END_OF_RECORD')
                        self.msg('sending : IAC DO OPT_END_OF_RECORD')
                        self.sock.send(IAC + DO + OPT_END_OF_RECORD)
                    elif opt == TRANSMIT_BINARY:
                        self.msg('IAC WILL TRANSMIT_BINARY')
                        self.msg('sending : IAC DO TRANSMIT_BINARY')
                        self.sock.send(IAC + DO + TRANSMIT_BINARY)
                    else:
                        self.msg('IAC WILL %d', ord(opt))
                        self.msg('sending : IAC DONT %d', ord(opt))
                        self.sock.send(IAC + DONT + opt)
                elif c  == WONT:
                    opt = self.rawq_getchar()
                    self.msg('IAC %s %d',
                             c == WILL and 'WILL' or 'WONT', ord(c))
                    self.sock.send(IAC + DONT + opt)
                elif c == SB:
                    sbOpt = self.rawq_getchar()
                    if sbOpt == TERMINAL_TYPE:
                        if self.rawq_getchar() == chr(1):
                            self.msg('sending: TERMINAL_TYPE')
                            self.sock.send(IAC + SB + TERMINAL_TYPE + \
                                           QUAL_IS + 'IBM-3179-2' + \
                                           IAC + SE)
                elif c == SE:
                    self.msg('ENDING Subnegotiation')
                else:
                    self.msg('IAC %s not recognized' % `c`)
                c = self.rawq_getchar()
        except EOFError: # raised by self.rawq_getchar()
            pass
        self.cookedq = self.cookedq + buf
        self.buffer = self.rawq

    def negotiate_session(self):
        self.process_negotiations()
        while not self.cookedq and not self.eof and self.sock_avail():
            self.fill_rawq()
            self.process_negotiations()

    def interact(self):
        """Interaction function, emulates a very dumb telnet client."""
        while 1:
            try:
                text = self.negotiate_session()
                if not text:
                    break
            except EOFError:
                break
        self.mt_interact()

    def mt_interact(self):
        """Multithreaded version of interact()."""
        import threading
        self.running = 1
        self.dataProducerThread = threading.Thread(target=self.listener)
        self.dataProducerThread.start()
        self.dataConsumerThread = \
                                threading.Thread(target=self.parse_stream)
        self.dataConsumerThread.start()

    def listener(self):
        """Helper for mt_interact() -- this executes in the other thread."""
        # load the first response from host
        self.loadStream(self.buffer)
        while self.running:
            try:
                #print 'listener running'
                self.read_incoming()
            except EOFError:
                print '*** Connection closed by remote host ***'
                return
        #print 'ended'

    def parse_stream(self):
        import struct
        import operator
        self.msg ('parse stream running')
        while self.running:
            self.dataStream = self.queue.get()
            if self.dataStream == None:
                #print 'data stream is None'
                self.running = 0
                continue
            # Check contents of message and do what it says
            # As a test, we simply print it
            self.msg( 'message from queue %s', `self.dataStream`)
            self.msgLen = ((ord(self.dataStream[0]) & 0xff) << 8) | \
                          (ord(self.dataStream[1]) & 0xff)
            opcode = ord(self.dataStream[9] )
            dataStart = 6 + ord(self.dataStream[6])
            self.pos = dataStart
            self.msg( 'opcode from stream buffer %s', `opcode`)
            self.msg( 'msg length from stream buffer %s', \
                      `self.msgLen`)
            self.msg( 'data start from stream buffer %s', `dataStart`)
            if opcode == 0:
                self.msg( 'No Operation ')
            elif opcode == 1:
                self.msg( 'Invite Operation ')
                self.parseIncoming()
            elif opcode == 2:
                self.msg( 'Output only ')
                self.parseIncoming()
            elif opcode == 3:
                self.msg( 'Put/Get Operation ')
                self.parseIncoming()
            elif opcode == 4:
                self.msg( 'Save Screen Operation ')
                self.parseIncoming()
            elif opcode == 5:
                self.msg( 'Restore Screen Operation ')
                self.parseIncoming()
            elif opcode == 6:
                self.msg( 'Read Immediate ')
            elif opcode == 7:
                self.msg( 'Reserved ')
            elif opcode == 8:
                self.msg( 'Read Screen Operation ')
            elif opcode == 9:
                self.msg( 'Reserved ')
            elif opcode == 10:
                self.msg( 'Cancel Invite ')
            elif opcode == 11:
                self.msg( 'Turn on message light ')
            elif opcode == 12:
                self.msg( 'Turn off message light ')
            else:
                self.msg( 'Invalid Operation Code ')
        self.msg('at end of queue')

    def parseIncoming(self):
        """Parse the incoming data stream."""
        buf = ''
        done = 0
        error = 0
        control0 = 0
        control1 = 0
        controlChars = 0
        while self.pos < self.msgLen and not done:
            self.pos += 1
            b = ord(self.dataStream[self.pos] )
            if b == 0 or b == 1 or b == 4:
                pass
            elif b == 2 or b == 3:
                self.msg( 'Save Screen')
            elif b == 7:
                self.msg( 'Audible bell')
                self.pos += 2
            elif b == 17:
                self.msg( 'Write to display')
                self.writeToDisplay(0)
            elif b == 18 or b == 19:
                self.msg( 'Restore Screen')
            elif b == 32:
                self.msg( 'Clear unit Alternate')
                self.screen.clearAll()
            elif b == 33:
                self.msg( 'Write Error Code')
            elif b == 34:
                self.msg( 'Write Error Code to Window')
            elif b == 64:
                self.msg( 'Clear Unit')
                self.screen.clearAll()
            elif b == 80:
                self.msg( 'Clear Format Table')
                self.screen.clearFFT()
            elif b == 98 or b == 102:
                self.msg( 'Read Screen Immediate')
            elif b == 66 or b == 82:
                self.msg( 'Read Input Fields or MDT Fields ')
                self.readType = b
                self.screen.goHome()
                self.screen.notify_screen_listeners(1)
            elif b == 83:
                self.msg( 'Read MDT Immediate Alt')
            elif b == 243:
                self.msg( 'Write Structured Field')
                self.writeStructuredField()
            else:
                self.msg( 'invalid option %s',b)

    def writeToDisplay(self,controlsExist):
        """Parse the incoming data stream."""
        pos = 0
        error = 0
        done = 0
        attr = 0
        nextOne = 0
        control0 = 0
        control1 = 0
        # initialize from Screen object later
        saRows = 24
        saColumns = 80
        if controlsExist:
            self.pos += 1
            control0 = self.dataStream[self.pos]
            self.pos += 1
            control1 = self.dataStream[self.pos]
        #print 'in write to display'
        while self.pos < self.msgLen and not done:
            self.pos += 1
            which1 = ord(self.dataStream[self.pos])
            if which1 == 1:    # Start of Header
                self.msg( 'Start of Header')
                error = self.processSOH()
            elif which1 == 2:    # Repeat to Address
                row = self.screen.getCurrentRow()
                col = self.screen.getCurrentCol()
                self.pos += 1
                toRow = ord(self.dataStream[self.pos])
                self.pos += 1
                toCol = (ord(self.dataStream[self.pos]) & 0xff)
                rows  = self.screen.getRows()
                cols = self.screen.getCols()
                if toRow >= row:
                    self.pos += 1
                    repeat = ord(self.dataStream[self.pos])
                    if row == 1 and col == 2 and toRow == rows and \
                       toCol == cols:
                        self.screen.clearAll()
                    else:
                        if repeat != 0:
                            repeat = self.getASCIIChar(repeat)
                        times = ((toRow * cols) + toCol) - \
                                ((row * cols) + col)
                        while times >= 0:
                            self.screen.setChar(repeat)
                            times -= 1
                self.msg( 'RA - Repeat to address %s, %s',toRow,toCol)
            elif which1 == 3:    # EA - Erase to address
                # need to implement later
                self.msg( 'Erase to Address')
            elif which1 == 4:    # Escape
                done = 1
                self.msg('Escape')
            elif which1 == 16:    # Transparent Data
                # need to implent later
                self.msg('Transparent Data')
            elif which1 == 17:    # SBA - Set buffer address
                self.pos += 1
                saRow = ord(self.dataStream[self.pos])
                self.pos += 1
                saCol = (ord(self.dataStream[self.pos]) & 0xff)
                self.screen.moveTo(saRow,saCol)
                self.msg('SBA - Set buffer Address %s %s',saRow,saCol)
            elif which1 == 18:    # WEA - Extended Attribute
                self.pos += 1
                self.dataStream[self.pos]
                self.pos += 1
                self.dataStream[self.pos]
                self.msg('WEA - Extended Attribute')
            elif which1 == 19 or which1 == 20 :    # IC - Insert Cursor
                                                   # MC - Move Cursor
                self.pos += 1
                icX = ord(self.dataStream[self.pos])
                self.pos += 1
                icY = (ord(self.dataStream[self.pos]) & 0xff)
                self.msg( 'IC or MC - Insert Cursor or Move Cursor \
                %s,%s',icX,icY)
                self.screen.setPendingInsert(1,icX,icY)
            elif which1 == 21:
                # WTDSF - Write to Display Structured Field order
                # implement later
                self.msg( 'WTDSF - \
                Write to Display Structured Field order')
            elif which1 == 29:    # SOF - Start of  field
                """Subtopic 15.6.12"""
                # lets initialize the Field format
                # word and field control word
                fcw1 = 0
                fcw2 = 0
                ffw1 = 0
                ffw0 = 0
                # get the first byte of the Field format word
                self.pos += 1
                ffw0 = ord(self.dataStream[self.pos])    # FFW0
                # The first two bits of this byte determine if the FFW
                # exits or not because it is optional we use a logical and
                # to get the value of the first two bits.  If the first
                # two bits contain the value 01 then we have a Field format
                # word.
                if (ffw0 & 0x40) == 0x40:
                    self.pos += 1
                    ffw1 = (ord(self.dataStream[self.pos]) & 0xff)  # FFW1
                    self.pos += 1
                    fcw1 = (ord(self.dataStream[self.pos]) & 0xff)
                    #check for field
                    # after processing the Field format word we check if
                    # the next byte is the field attribute byte or not.
                    # If it is not an attribute byte then we have a field
                    # control word and the attribute will follow the next
                    # two bytes.
                    if not self.isAttribute(fcw1):
                        self.pos += 1
                        fcw2 = (ord(self.dataStream[self.pos]) & 0xff)
                        # FCW2
                        self.pos += 1
                        attr = (ord(self.dataStream[self.pos]) & 0xff)
                        # attribute
                    else:
                        attr = fcw1    # attribute of field
                        fcw1 = 0
                else:
                    # If the check for the Field format word was not
                    # successful then we just use the byte read as the
                    # field attribute
                    attr = ffw0
                # We then parse the length of the field by using the next
                # to bytes.  Shifting the first byte and using logical or
                # of the next byte will obtain us the length of the field
                fLength = ((ord(self.dataStream[self.pos + 1]) & 0xff) \
                           << 8) | (ord(self.dataStream[self.pos + 2]) \
                                    & 0xff)
                self.pos += 2
                self.screen.addField(attr,fLength,ffw0,ffw1,fcw1,fcw2)
                self.msg(' Start of field with <length %s> <ffw0 %s> \
                <ffw1 %s> <fcw1 %s> <fcw2 %s>',fLength,ffw0,ffw1,fcw1,fcw2)
            else:
                byte0 = (ord(self.dataStream[self.pos]) & 0xff)
                if self.isAttribute(byte0):
                    self.screen.setAttr(byte0)
                elif byte0 < 64:
                    self.screen.setChar(byte0)
                else:
                    self.screen.setChar(self.getASCIIChar(byte0))
            if error:
                done = 1
        return error

    def processSOH(self):
        """ Process start of header information """
        self.pos += 1
        len = ord(self.dataStream[self.pos])
        if len > 0 and len <= 7:
            self.pos += 1
            self.dataStream[self.pos]    # flag byte 2
            self.pos += 1
            self.dataStream[self.pos]    # Reserved
            self.pos += 1
            self.dataStream[self.pos]    # Resequence fields
            # add support for parse error line later
            self.pos += 1
            self.dataStream[self.pos]    # Error line
            byte1 = 0
            if len >= 5 :
                self.pos += 1
                byte1 = ord(self.dataStream[self.pos])
            if len >= 6 :
                self.pos += 1
                byte1 = ord(self.dataStream[self.pos])
            if len >= 7 :
                self.pos += 1
                byte1 = ord(self.dataStream[self.pos])
            return 0
        else:
            return 1

    def isAttribute(self,byte):
        """ Check if the byte is an attribute byte or not """
        return (byte & 0xe0) == 0x20;

    def getASCIIChar(self,byte):
        return self.codePage.ebcdic2uni(byte)

    def setScreen(self,screen):
        self.screen = screen

    def sendAidKey(self,aid):
        """
        Send aid key and associated field format data to host
        """
        boasp = []
        boasp.append(self.screen.getCurrentRow())
        boasp.append(self.screen.getCurrentCol())
        boasp.append(aid)
        self.screen.getFields().readFormatTable(boasp,self.readType,self.codePage)
        self.writeGDS(0,3,boasp)

    def writeStructuredField(self):
        """
        Write structured field for query message response
        """
        length = ((ord(self.dataStream[self.pos + 1]) & 0xff) \
                   << 8) | (ord(self.dataStream[self.pos + 2]) \
                            & 0xff)
        self.pos += 2
        #print length
        self.pos += 1
        StartOfHeaderOrder = ord(self.dataStream[self.pos])
        #print StartOfHeaderOrder
        self.pos += 1
        queryrequest = ord(self.dataStream[self.pos])
        print queryrequest
        self.pos += 1
        ord(self.dataStream[self.pos])
        print 'now lets send query response'
        self.sendQueryResponse()

    def sendQueryResponse(self):
        """
            The query command is used to obtain information about the capabilities
            of the 5250 display.
            The Query command must follow an Escape (0x04) and Write Structured
            Field command (0xF3).
            This section is modeled after the rfc1205 - 5250 Telnet Interface section
            5.3
        """
        abyte = []
        abyte.append(0x00)  ## Cursor row column set to 0,0
        abyte.append(0x00)
        abyte.append(0x88)  ## 0x88 inbound write structure field aid
        abyte.append(0x00)  ## length of query response
        abyte.append(0x3A)  ##   Set to 58 for normal emulation
        abyte.append(0xD9)  ## command class
        abyte.append(0x70)  ## command type query
        abyte.append(0x80)  ## Flag byte
        abyte.append(0x06)  ## controller hardware class
        abyte.append(0x00)  ## 0x0600 - other WSF or another 5250 emulator
        abyte.append(0x01)  ## Controller Code Level
        abyte.append(0x01)
        abyte.append(0x00)
        abyte.append(0x0) ## 13 - 28 are reserved
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x01) ## device type - 0x01 5250 Emulator
        abyte.append(ord(self.codePage.uni2ebcdic('5'))) ## device type character
        abyte.append(ord(self.codePage.uni2ebcdic('2')))
        abyte.append(ord(self.codePage.uni2ebcdic('5')))
        abyte.append(ord(self.codePage.uni2ebcdic('1')))
        abyte.append(ord(self.codePage.uni2ebcdic('0')))
        abyte.append(ord(self.codePage.uni2ebcdic('1')))
        abyte.append(ord(self.codePage.uni2ebcdic('1')))
        abyte.append(0x02) ## keyboard id - 0x02 Standard Keyboard
        abyte.append(0x00) ## extended keyboard id
        abyte.append(0x00) ## reserved
        abyte.append(0x00) ## 40 - 43 Display Serial Number
        abyte.append(36)
        abyte.append(36)
        abyte.append(0x00)
        abyte.append(0x01)  ## Maximum number of display fields - 256
        abyte.append(0x00)  ## 0x0100
        abyte.append(0x0)   ## 46 - 48 reserved set to 0x00
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x01)  ## 49 - 53 Controller Display Capability
        abyte.append(16)
        abyte.append(0x0)
        abyte.append(0x0)
        """
          53
          Bit 0-2: B'000'   -  no graphics capability
                   B'001'   - 5292-2 style graphics
          Bit 3-7: B '00000' = reserved (it seems for Client access)
        """
        abyte.append(0x0)  ## 0x0 is normal emulation
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        abyte.append(0x0)
        self.writeGDS(0,0,abyte)

def test():
    """Test program for tnvtlib.
    Usage: python tnvtlib.py [-d] ... [host [port]]
    Default host is localhost; default port is 23.
    """
    import signal
    import Screen5250
    debuglevel = 0
    while sys.argv[1:] and sys.argv[1] == '-d':
        debuglevel = debuglevel+1
        del sys.argv[1]
    host = 'localhost'
    if sys.argv[1:]:
        host = sys.argv[1]
    port = 0
    if sys.argv[2:]:
        portstr = sys.argv[2]
        try:
            port = int(portstr)
        except ValueError:
            port = socket.getservbyname(portstr, 'tcp')
    tn = vt5250()
    tn.set_debuglevel(debuglevel)
    tn.setScreen(Screen5250.Screen5250())
    tn.open(host, port)
    while tn.running:
       pass
    tn.close()
    print 'I am here'
    sys.exit
    print 'After exit'

    def onSignal(signum, stackFrame):
        """
        Let's capture the signals and close connections
        so we do not get zombie processes.
        """
        tn.close()

if __name__ == '__main__':
    test()
