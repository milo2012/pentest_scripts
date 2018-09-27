#!/usr/bin/python
'''
$ python sniffCert.py -h
Usage: sniffCert.py [options]

Options:
  -h, --help      show this help message and exit
  -i INTERFACENO  Interface to sniff
  
$ python sniffCert.py -i en0
[*] Sniffing Packets on Interface: en0
[*] Connected to: networkid=Wireless_Test
[*] Sent credentials: XXXXX
[+] EAP Type: Protected EAP (EAP-PEAP)
[+] Found Certificate
[+] Writing certificate to sslcert.der
[+] Display details of SSL certificate
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:

'''
import os
import optparse
import binascii
from scapy.all import *

eapTypeList=[]
eapTypeList.append([25,"Protected EAP (EAP-PEAP)"])

def http_header(packet):
	try:
		if packet[EAP].code==2:
			if packet[EAP].type==1:
				print "[*] Sent credentials: "+packet[EAP].identity
		if packet[EAP].code==1:
			try:
				if packet[EAP].type==1:
					tmpReq=packet[EAP].message
					if "networkid=" in tmpReq and "," in tmpReq:
						tmpList=tmpReq.split(",") 
						for x in tmpList:
							if "networkid=" in x:
								connectedSSID=x.split("networkid=")[1]
								print "[*] Connected to: "+connectedSSID

				data=binascii.hexlify(packet[EAP].load)
				if data.startswith("0116"):
					if packet[EAP].type==25:
						for x in eapTypeList:
							if x[0]==packet[EAP].type:
								print "[+] EAP Type: "+x[1]
					print "[+] Found Certificate"
					dataSSLCert=""
					tmpList=data.split("3082")
					count=0
					for x in tmpList:
						if count>0:
							tmpData="3082"+x
							dataSSLCert+=tmpData
						count+=1
					if len(dataSSLCert)>0:		
						print "[+] Writing certificate to sslcert.der"
						with open('sslcert.der','wb') as f:
							f.write(binascii.unhexlify(dataSSLCert))
						if os.path.exists('sslcert.der'):
							print "[+] Display details of SSL certificate"
							cmd="openssl x509 -inform DER -in sslcert.der -text"
							os.system(cmd)
			except AttributeError:
				pass			
		#print packet.show()       
	except IndexError:
		pass


parser = optparse.OptionParser()
parser.add_option('-i', action="store", dest="interfaceNo", help="Interface to sniff")
options, remainder = parser.parse_args()
if not options.interfaceNo:
	print "[-] Please use the -i option"
	sys.exit()
interfaceNo=options.interfaceNo
print "[*] Sniffing Packets on Interface: "+interfaceNo
a=sniff(iface=interfaceNo,filter='ether proto 0x888e', prn=http_header , count=999, store=1)
