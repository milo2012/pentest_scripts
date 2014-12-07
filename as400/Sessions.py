"""
SessionManager and Sessions objects
Created by Nathanael Custer 2002-07-01
"""
from Session import Session

__all__ = ["Sessions"]

# Tunable parameters
DEBUGLEVEL = 0
# Telnet Port
TELNET_PORT = 23

class Sessions:
    def __init__(self):
        self.list = []

    def _addSession(self, name=''):
        session = [name, Session()]
        self.list.append(session)

    def _delSession(self, name=''):
        for x in self.list:
            if name == x[0]:
                self.list.remove(x)
            #else:
                #raise error here

    def item(self, name=''):
        for x in self.list:
            if name == x[0]:
                return x[1]

    def item_index(self, index=0):
        return self.list[index][1]

    def _list(self):
        return self.list