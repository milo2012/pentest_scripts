#!/usr/local/bin/python
#########################################################################
#                 Tk8.0 style main window menus                         #
#########################################################################

from Tkinter import *                           # get widget classes
from tkMessageBox import *                      # get standard dialogs
from tkSimpleDialog import askstring
import Session
import Screen5250
import ScreenFields
from SessionManager import SessionManager
#import Sessions
import CodePage
from sys import argv

__all__ = ["testsession"]

class StartFrame(Frame):                          # an extended frame
    def __init__(self, parent=None):               # attach to top-level?
        self.first = 1
        self.USERID = None
        self.PASSWORD = None
        self.myScreen = None

        Frame.__init__(self, parent)               # do superclass init
        self.canvas = Canvas(parent,width=600,height=500, bg='black')
        self.manager = SessionManager()
        self.pack()

        self.createWidgets()                       # attach frames/widgets
        self.master.title("TN5250 for Python - Testing")
        self.master.iconname("TN5250") # label when iconified
        self.strprg()

    def outputScreen(self, initiator, startRow, startColumn, endRow, endColumn):
	"""
        Callable method to get screen updates
        """
        print 'ScreenUpdated - initiated from ', initiator, \
              ' Starting from -> ',startRow,endRow,' to -> ', \
              endRow,endColumn

        if initiator == 0:  ## 0  is from client and 1 is from host
            return

        # Note we only print the first 12 rows here
        indices = range(1,24)

        # for idx in indices:
        #     print self.myScreen.getPlaneData(idx,1,idx,80,1)
        #     print self.screen.getPlaneData(idx,1,80,2)

        fields = self.myScreen.getFields()

        if self.USERID == None or self.PASSWORD == None:
            self.USERID = raw_input("What's your username ? > ")
            self.PASSWORD = raw_input("What's your password ? > ")

        if self.first == 1:
            field = fields.getItem(0)
            field.setString(self.USERID)
            field = fields.getItem(1)
            field.setString(self.PASSWORD)

        for field in fields:
            #print field.toString()
            print field.getText()

            #print fields.readFormatTable(0x42,CodePage.CodePage())
            #print myScreen.getFields().readFormatTable(0x52,CodePage.CodePage())
        # Note we only print the first 12 rows here
        indices = range(1,25)
        row = 0

        for idx in indices:
            text = self.myScreen.getPlaneData(idx,1,idx,80,1)
            row += 15
            col = 0
            indx = range(0,79)
            for x in indx:
                col += 10
                self.canvas.create_text(col,row,text=text[x], anchor=E, fill='green')

        print 'number of fields',self.myScreen.getFields().getCount()
        """
            Patrick here I just keep pressing enter so that the screens
            keep coming up to see the messages.  Actually 6 times.
            the first is to send username and password.  Then 2 more times
            to get passed messages and stuff.  Then 2 more times to
            get messages at the bottom of the screen to make sure all is
            coming up.  Change this number if you want less for now.
        """

        if self.first < 7:
            self.myScreen.sendAidKey(0xF1)
            self.first += 1

    def strprg(self):
        if len(argv) >= 2: host = argv[1]
        else:
            host = askstring('Hostname', "Name of the Host ?")

        #ts = testsession()

        if len(argv) > 3:
            self.USERID = argv[2]
            self.PASSWORD = argv[3]

        session = self.manager.openSession('Session 1')
        session.setHost(host)      
        #session = Session.Session(host)

        session.set_debuglevel(1)
        self.myScreen = session.getScreen()
        session.getScreen().add_screen_listener(self.outputScreen)
        session.connect()

    def createWidgets(self):
        self.makeMenuBar()
        #self.canvas = self.root.createcomponent('canvas', (), None, \
        #Canvas, (self.interior(),), width=self.width, \
        #height=self.height,background="black")
        self.canvas.pack(fill=BOTH)
        #text = Text(self, relief=SUNKEN, fg='green', bg='black', \
        #width=150, height=50)
        #text.pack(fill=BOTH)

    def makeMenuBar(self):
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)    # master=top-level window
        self.fileMenu()
        self.editMenu()

    def fileMenu(self):
        pulldown = Menu(self.menubar, tearoff=0)
        pulldown.add_command(label='Open...', command=self.notdone, \
                             underline=0)
        pulldown.add_command(label='Quit',    command=self.quit,    \
                             underline=0)
        pulldown.entryconfig(0, state=DISABLED)
        self.menubar.add_cascade(label='File', underline=0, menu=pulldown)

    def editMenu(self):
        pulldown = Menu(self.menubar, tearoff=0)
        pulldown.add_command(label='Copy',   command=self.notdone)
        pulldown.add_command(label='Paste',    command=self.notdone)
        pulldown.entryconfig(0, state=DISABLED)
        pulldown.entryconfig(1, state=DISABLED)
        self.menubar.add_cascade(label='Edit', underline=0, menu=pulldown)

    def notdone(self):
        showerror('Not implemented', 'Not yet available')

    def quit(self):
        if askyesno('Verify quit', 'Are you sure you want to quit?'):
            Frame.quit(self)

if __name__ == '__main__':
    #root = Tk()
    StartFrame().mainloop()
    #root.mainloop()  # if I'm run as a script
