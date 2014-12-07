import argparse
import time
import sys
import Session
import Screen5250
import ScreenFields
import CodePage
from sys import argv
__all__ = ["testsession"]
myScreen = None
foundText = ""
class testsession:
    def __init__(self):
        self.first = 1
        self.USERID = None
        self.PASSWORD = None
    def outputScreen(self,initiator,startRow,startColumn,endRow,endColumn):
        """
        Callable method to get screen updates
        """
        #print 'ScreenUpdated - initiated from ',initiator, \
        #      ' Starting from -> ',startRow,endRow,' to -> ',endRow,endColumn
        if initiator == 0:  ## 0  is from client and 1 is from host
            return
        # Note we only print the first 12 rows here
        indices = range(1,24)
        #for idx in indices:
            #print myScreen.getPlaneData(idx,1,idx,80,1)
            #print self.screen.getPlaneData(idx,1,80,2)
        fields = myScreen.getFields()
        if self.USERID == None or self.PASSWORD == None:
            self.USERID = raw_input("What's your username ? > ")
            self.PASSWORD = raw_input("What's your password ? > ")
        if self.first == 1:
            field = fields.getItem(0)
            field.setString(self.USERID)
            field = fields.getItem(1)
            field.setString(self.PASSWORD)
        #for field in fields:
        #    print field.toString()
        #    #print field.getText()

        #print fields.readFormatTable(0x42,CodePage.CodePage())
        #print myScreen.getFields().readFormatTable(0x52,CodePage.CodePage())
        # Note we only print the first 12 rows here
        indices = range(1,25)
	global foundText
        for idx in indices:
            output = myScreen.getPlaneData(idx,1,idx,80,1)
	    if "does not exist" in output:
	    	foundText=output
	    if "cannot sign on" in output:
		foundText=output
	    if "No password associated" in output:
		foundText=output
	#if len(foundText.strip())>0:
	#	print foundText
	#else:
	#	print "It might be possible to login with ("+self.USERID+"|"+self.PASSWORD+")"
        #print myScreen.getPlaneData(idx,1,idx,80,1)
		
        #print 'number of fields',myScreen.getFields().getCount()
        if self.first < 7:
            myScreen.sendAidKey(0xF1)
            self.first += 1
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',dest='hostIP',action='store',help='[IP of AS/400 host]')
    parser.add_argument('-p',dest='portNo',action='store',help='[Port of AS/400 host]')
    options = parser.parse_args()
    
    if len(sys.argv)==1:
    	parser.print_help()
	sys.exit()
    else:
 	if options.hostIP and options.portNo:
    		userList=[]
    		userList.append(('QSECOFR','QSECOFR'))
    		userList.append(('QPGWR','QPGWR'))
    		userList.append(('QUSER','QUSER'))
    		userList.append(('QSYSOFR','QSYSOFR'))
    		userList.append(('QSRVBAS','QSRVBAS'))
    		userList.append(('QSRV','QSRV'))
    		userList.append(('QDFTOWN','QDFTOWN'))

		host = options.hostIP

    		for user in userList:
        		ts = testsession()
			ts.USERID = user[0]
        		ts.PASSWORD = user[1]
			print "\n[*] Testing ("+user[0]+"|"+user[1]+")"
    			session = Session.Session(host)
			session.setPort = options.portNo
    			session.set_debuglevel(0)
    			myScreen = session.getScreen()
    			session.getScreen().add_screen_listener(ts.outputScreen)
    			session.connect()
			time.sleep(2)
			if len(foundText.strip())>0:
				print foundText
			else:
				print "It might be possible to login with ("+user[0]+"|"+user[1]+")"

			session.disconnect()
    		sys.exit() 
 
