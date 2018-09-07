import argparse
import urllib2, socket,sys,base64,os
from xml.dom.minidom import parse, parseString
import socket
from urlparse import urlparse
import commands


bingAPIKey = '40Mem6C6yp/FDmkBYaCtgEs7GdiNIGeod+n7T8ol2x0'

def isOpen(ip,port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	try:
     		s.connect((ip, int(port)))
     		s.shutdown(2)
     		return True
    	except:
     		return False


def RunCommand(fullCmd):
    try:
        #print fullCmd
        return commands.getoutput(fullCmd)
    except:
        return "Error executing command %s" %(fullCmd)


def getIP(domain):
    try:
    	return socket.gethostbyname(domain)
    except socket.gaierror:
	return ""
def getSSLcertname(ip):
	fullCmd = "nmap --script=ssl-cert -p 443 "+ip
        results = RunCommand(fullCmd)
       	resultsList = results.split("\n")
       	for line in resultsList:
        	if "| ssl-cert: Subject: commonName=" in line and "*." not in line:
			hostName = line.replace("| ssl-cert: Subject: commonName=","").split("/")[0]
                      	hostName = hostName.strip()
			if hostName:
				return hostName

def reverseBing(ip): 
    sites = []
    skip = 0
    top = 100
    port = 443
    if isOpen(ip,port):
	if getSSLcertname(ip):
		sites.append(getSSLcertname(ip))
    while skip < 200:
	 try:
         	url = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query='ip:%s'&$top=%s&$skip=%s&$format=Atom"%(ip,top,skip)
         	request = urllib2.Request(url)
         	auth = base64.encodestring("%s:%s" % (bingAPIKey, bingAPIKey)).replace("\n", "")
         	request.add_header("Authorization", "Basic %s" % auth)
         	res = urllib2.urlopen(request)
         	data = res.read()
	
        	xmldoc = parseString(data)
        	site_list = xmldoc.getElementsByTagName('d:Url')
        	for site in site_list:
        	      	domain = site.childNodes[0].nodeValue
              		domain = domain.split("/")[2]
	      		tmpDomain = domain
	      		if ":" in domain:
				domain = domain.split(":")[0]
              		if tmpDomain not in sites:
				siteIP = getIP(domain)
	   		 	if ip not in sites:
					#if ip!=siteIP:
			  		#	 sites.append(ip)
		 			if ip==siteIP:
	                			sites.append(tmpDomain)
	 except urllib2.URLError:
			continue
         skip += 50
    return sites	

parser = argparse.ArgumentParser(description='IP to DNS Name')
parser.add_argument('-host', help='Enter an IP address or Domain name')
parser.add_argument('-file', help='File containing list of IP addresses')
args = parser.parse_args()
if args.host==None and args.file==None:
	print "\n[!] Please run 'python "+sys.argv[0]+" -h'\n"
	sys.exit()
else:
	if args.file:
		filename = args.file
		ipList = []
		with open(filename) as f:
    			ipList = f.read().splitlines()
		for host in ipList:
			tmpHost = host
    			if "http" in tmpHost or "https" in tmpHost:
				parse_object = urlparse(tmpHost)
				fqdn = str(parse_object.hostname)
				tmpHost = fqdn
			if any(c.isalpha() for c in tmpHost)==False:
				if len(bingAPIKey)<1:
					sys.exit("[!] Please check your bingAPIKey !")
				sites = reverseBing(tmpHost)
				if sites:
					for site in sites:
						if site!=None:
							print tmpHost+"\t"+site
						else:
							print tmpHost
				else:
					print tmpHost
	elif args.host:
		tmpHost = args.host
    		if "http" in tmpHost or "https" in tmpHost:
			parse_object = urlparse(tmpHost)
			fqdn = str(parse_object.hostname)
			tmpHost = fqdn
		if any(c.isalpha() for c in tmpHost)==False:
			if len(bingAPIKey)<1:
				sys.exit("[!] Please check your bingAPIKey !")
			sites = reverseBing(tmpHost)
			for site in sites:
				print tmpHost+"\t"+site
