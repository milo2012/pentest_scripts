#!/usr/bin/env python
import re,sys,os,subprocess,shlex,Queue
from threading import Thread
import urllib2, socket,sys,base64,ssl
from xml.dom.minidom import parse, parseString

niktoPath = "/pentest/nikto-2.1.5/nikto.pl"
#Bing Search API Account Key
account_key = ""
runBing = True

#CA certs http://curl.haxx.se/ca/cacert.pem

class Consumer(Thread):
 def __init__(self, queue=None):
  super(Consumer, self).__init__()
  self.daemon = True
  self.queue = queue
 def run(self):
  while True:
   cmd = self.queue.get()
   args = shlex.split(cmd)
   p = subprocess.Popen(args,stdout=subprocess.PIPE)
   retcode = p.wait()
   #p.communicate()
   self.queue.task_done()

def isOpen(ip,port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((ip,int(port)))
		s.shutdown(2)
		return True
	except:	
		return False
		
def getSSLCommonName(HOST,PORT):
    try:
        HOST = socket.getaddrinfo(HOST, PORT)[0][4][0]
        sock = socket.socket()
        sock.connect((HOST, PORT))
        sock = ssl.wrap_socket(sock,
        #cert_reqs=ssl.CERT_REQUIRED,
        cert_reqs=ssl.CERT_OPTIONAL,
        #cert_reqs=ssl.CERT_NOT_REQUIRED,
        ca_certs="cacert.pem"
        )
        cert = sock.getpeercert()
        for field in cert['subject']:
            if field[0][0] == 'commonName':
                certhost = field[0][1]
                return certhost   
    except ssl.SSLError:
        return ""
        
def bing(account_key,ip):
    if(isinstance(ip,list)):
        for count in ip:
            count = count.strip()
            sites = []
            skip = 0
            top = 50
            while skip < 200:
                  url = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query='ip:%s'&$top=%s&$skip=%s&$format=Atom"% (count,top,skip)
                  request = urllib2.Request(url)
                  auth = base64.encodestring("%s:%s" % (account_key, account_key)).replace("\n", "")
                  request.add_header("Authorization", "Basic %s" % auth)
                  res = urllib2.urlopen(request)
                  data = res.read()

		  tempDomainList = []
                  xmldoc = parseString(data)
                  site_list = xmldoc.getElementsByTagName('d:Url')
                  for site in site_list:
                      domain = site.childNodes[0].nodeValue
                      domain = domain.split("/")[2]
                      if domain not in sites:
			 if domain not in tempDomainList:
	                         tempDomainList.append(domain)
        	                 #sites.append(domain)
		  count = 1
		  if len(tempDomainList)>1:
			for i in tempDomainList:
				print "("+str(count)+")\t"+i
				count+=1
                  	#print tempDomainList
			print "[*] Enter the number followed by comma E.g. 1, 4, 10"
			print "[*] To select all, key in 'ALL'. Leave it blank or key in 'NONE' to ignore all."
	                listInput = raw_input()
 		        listInput = listInput.strip()
			listInput = listInput.lower()		
			if len(listInput)>0:	
			  	if listInput == "all" and listInput != "none":
					for x in tempDomainList:
						sites.append(x)
				elif listInput != "all" and listInput != "none":
					inputList = listInput.split(",")
					for x in inputList:
						print tempDomainList[int(x)-1]
						sites.append(tempDomainList[int(x)-1])
                  skip += 50

            if(len(sites)==0):    
                if isOpen(count,443):
                    commonName=""
                    commonName=getSSLCommonName(count,443)         
                    if(len(commonName)>0):
                        sites.append(commonName)            
            return sites
            
    elif(isinstance(ip,str)):
        sites = []
        skip = 0
        top = 50
        while skip < 200:
              url = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query='ip:%s'&$top=%s&$skip=%s&$format=Atom"% (ip,top,skip)
              request = urllib2.Request(url)
              auth = base64.encodestring("%s:%s" % (account_key, account_key)).replace("\n", "")
              request.add_header("Authorization", "Basic %s" % auth)
              res = urllib2.urlopen(request)
              data = res.read()

              xmldoc = parseString(data)
              site_list = xmldoc.getElementsByTagName('d:Url')
	      tempDomainList = []
              for site in site_list:
                  domain = site.childNodes[0].nodeValue
                  domain = domain.split("/")[2]
                  if domain not in sites:
		     	if domain not in tempDomainList:
		     		tempDomainList.append(domain)
                     		#sites.append(domain)
	      count = 1
              if len(tempDomainList)>1:
	      	  for i in tempDomainList:
	      	     print "("+str(count)+")\t"+i
		     count+=1
		  print "[*] Enter the number followed by comma E.g. 1, 4, 10"
		  print "[*] To select all, key in 'ALL'. Leave it blank or key in 'NONE' to ignore all."
	          listInput = raw_input()
		  listInput = listInput.strip()
		  listInput = listInput.lower()
		  if len(listInput)>0:
			  if listInput == "all" and listInput != "none":
				for x in tempDomainList:
					sites.append(x)
			  elif listInput != "all" and listInput != "none":
				inputList = listInput.split(",")
				for x in inputList:
					print tempDomainList[int(x)-1]
					sites.append(tempDomainList[int(x)-1])

              #if len(tempDomainList)>1:
	      #	      print tempDomainList
              skip += 50
        if(len(sites)==0):
            if isOpen(ip,443):
                commonName=""
                commonName=getSSLCommonName(ip,443)         
                if(len(commonName)>0):
                    sites.append(commonName)
        return sites
    
def parseNmap(fname,child,displayOnly):
 queue = Queue.Queue()
 ipList = []
 with open(fname) as f:
  count=0
  content = f.readlines()
  for i in content:
   count+=1
   if(count>2):
     i = i.strip()
     if 'http' in i:
      result = re.search('Host:(.*)\(\)', i)
      host = result.group(1).strip()
      if host not in ipList:
       ipList.append(host)
      #Perform a reverse DNS lookup on Bing.com        
       sites = []
       global runBing
       if runBing==True:
        try:
         sites = bing(account_key,host)
        except urllib2.HTTPError:
         print "[*] Please check your Bing API Key"
         sys.exit(0)
       if len(sites)>0:
           for site in sites:
               strStart = i.index('Ports: ')+7
               strEnd   = len(i)
               portString = i[strStart:strEnd]
               portStringList = portString.split(",")
               for port in portStringList:
                portNo = port.split("/")[0].strip()
               if "ssl|http" in port:
                if "open" in port:
                 currentDir = os.getcwd()
                 savePath = currentDir+"/nikto-"+host+"-port"+portNo+"-"+site+".txt"
                 cmd = "/usr/bin/perl "+niktoPath+" -vhost "+site+" -maxtime 7200 -Cgidirs all -ssl -host "+host+" -port "+portNo+" -output "+savePath
                 print cmd
                 queue.put(cmd)
               elif "http" in port:
                if "open" in port:
                 currentDir = os.getcwd()
                 savePath = currentDir+"/nikto-"+host+"-port"+portNo+"-"+site+".txt"
                 cmd = "/usr/bin/perl "+niktoPath+" -vhost "+site+" -maxtime 7200 -Cgidirs all -host "+host+" -port "+portNo+" -output "+savePath
                 print cmd
                 queue.put(cmd)                 
       else:
           strStart = i.index('Ports: ')+7
           strEnd   = len(i)
           portString = i[strStart:strEnd]
           portStringList = portString.split(",")
           for port in portStringList:
            currentDir = os.getcwd()
            portNo = port.split("/")[0].strip()
            savePath = currentDir+"/nikto-"+host+"-port"+portNo+".txt"
            if "ssl|http" in port:             
             if "open" in port:
              cmd = "/usr/bin/perl "+niktoPath+" -maxtime 7200 -Cgidirs all -ssl -host "+host+" -port "+portNo+" -output "+savePath
              print cmd
              queue.put(cmd)
            elif "http" in port:
             if "open" in port:
              cmd = "/usr/bin/perl "+niktoPath+" -maxtime 7200 -Cgidirs all -host "+host+" -port "+portNo+" -output "+savePath
              print cmd
              queue.put(cmd)   
 if displayOnly==False:    
  for i in range(int(child)):
   consumer = Consumer(queue)
   consumer.start()
  queue.join()
 
def options(arguments):
 count = 0
 child = 0
 displayOnly = False
 filename = ""
 for arg in arguments:
  if arg == "-child":
   child = arguments[count+1]
  if arg == "-file":
   filename = arguments[count+1]
  if arg == "-nobing":
   global runBing
   runBing = False
  if arg == "-display":
   displayOnly = True
  count+=1  
 print filename
 parseNmap(filename,child,displayOnly)

def showhelp():
 print """
#####################################################
#                  niktoHelper.py 	            #
# Run Nikto against http/https services in .gnmap   #
#           visit milo2012.wordpress.com            #
#####################################################
Usage: python niktoHelper.py [OPTIONS]

[OPTIONS]

-file   [Nmap .gnmap File]
-child  [Num of Threads]
-nobing [Do not run Bing reverse IP]
-display[Print only to screen. Do not run Nikto]
"""

if __name__ == '__main__':
 if len(sys.argv) <= 2:
  showhelp()
  sys.exit()
 else:
  options(sys.argv)
