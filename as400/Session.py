"""
Session object
Created by Kenneth J. Pouncey 2002-05-19
"""
from vt5250 import vt5250
from Screen5250 import Screen5250

__all__ = ["Session"]

# Tunable parameters
DEBUGLEVEL = 0
# Telnet Port
TELNET_PORT = 993

class Session:
    """Session interface class."""
    def __init__(self,host=None,port=0):
        """Constructor."""
        self.debuglevel = DEBUGLEVEL
        self.vt = vt5250()
        self.vt.set_debuglevel(self.debuglevel)
        self.screen = Screen5250()
        self.screen.set_debuglevel(self.debuglevel)
        self.vt.setScreen(self.screen)
        self.screen.setVT(self.vt)
        if host:
            self.host = host
        else:
            self.host = 'localhost'
        if port:
            self.setPort(port)
        else:
            self.port = TELNET_PORT

    def set_debuglevel(self, debuglevel):
        """
        Set the debug level.
        The higher it is, the more debug output you get (on sys.stdout).
        """
        self.debuglevel = debuglevel
        self.vt.set_debuglevel(self.debuglevel)
        self.screen.set_debuglevel(self.debuglevel)

    def connect(self):
        self.vt.open(self.host,self.port)

    def disconnect(self):
        self.vt.close()

    def setHost(self,host):
        self.host = host

    def setPort(self,port):
        try:
            self.port = int(port)
        except ValueError:
            self.port = TELNET_PORT

    def getScreen(self):
        return self.screen
