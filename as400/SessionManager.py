"""
SessionManager and Sessions objects
Created by Nathanael Custer 2002-07-01
"""
from Sessions import Sessions

__all__ = ["SessionManager"]

# Tunable parameters
DEBUGLEVEL = 0
# Telnet PortTELNET_PORT = 23

class SessionManager:
    def __init__(self):
        self.MasterSessionList = Sessions()

    def getSessions(self):
        return self.MasterSessionList

    def openSession(self, name=''):
        self.MasterSessionList._addSession(name)
        return self.MasterSessionList.item(name)

    def closeSession(self, name=''):
        session = self.MasterSessionList.item(name)
        self.MasterSessionList._delSession(name)

    def refresh(self):
        return self.MasterSessionList

if __name__ == '__main__':
    test = SessionManager()
    print "Generating 10 test sessions."
    for x in range(10):
        test.openSession('test' + str(x))
    print "Here is the list of the sessions:"
    a = test.getSessions()
    print a.list
    print "Now removing the sessions one at a time"
    for x in range(10):
        test.closeSession('test' + str(x))
        a = test.refresh()
        print "One less"
        print a.list
