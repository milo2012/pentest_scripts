import cx_Oracle
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

#http://hivelocity.dl.sourceforge.net/project/cx-oracle/5.1.1/cx_Oracle-5.1.1.tar.gz
outputFileCSV=""
ccRegex = []
ccRegex.append("^4[0-9]{12}(?:[0-9]{3})?$")		#Visa Regex	
ccRegex.append("^5[1-5][0-9]{14}$")			#Mastercard Regex
ccRegex.append("^3[47][0-9]{13}$")			#Amex Regex
ccRegex.append("^3(?:0[0-5]|[68][0-9])[0-9]{11}$")	#Diners Regex
ccRegex.append("^6(?:011|5[0-9]{2})[0-9]{12}$")		#Discover Regex		
ccRegex.append("^(?:2131|1800|35\d{3})\d{11}$")		#JCDB Regex

interestingData = False

def cardLuhnChecksumIsValid(card_number):
    """ checks to make sure that the card passes a luhn mod-10 checksum """

    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])

        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit
    return ( (sum % 10) == 0 )
    
def dataExtract(username,password,hostname,sid,sample):
	print "[+] Extracting data from database"
	try:
		orcl1 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
		curs = orcl1.cursor()	
		curs.execute("select * from v$database")
		for db_data in curs:
			#Iterate per database
			dbName = db_data[1]
			print "[+] Database found: "+dbName
			
			orcl2 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
			curs2 = orcl2.cursor()
			tblCount2 = curs2.execute("SELECT COUNT(*) FROM tab")	
			#Get a count of the total tables in the databases
			if tblCount2<1:
				print "There are no tables in "+dbName+". Its possible that the account does not have access. Try escalating privileges."
			if tblCount2:
				#Continue with CC data search	
				orcl3 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
				curs3 = orcl3.cursor()	
				curs3.execute("SELECT * FROM tab")	#Get a list of all tables
				for row_data in curs3:
					#Iterate per table 
					if not row_data[0].startswith('BIN$'): # skip recycle bin tables
						tableName = row_data[0]
						try:
							print colored("\n[+] Ransacking table: "+tableName+" in "+sid,"red",attrs=['bold'])
							orcl4 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
							sql4 = "select * from (select * from  " + tableName+") where rownum <="+str(sample)
							curs4 = orcl4.cursor()
							curs4.execute(sql4)
							matchedRows = []
							results = curs4.fetchall()
						except cx_Oracle.DatabaseError:
							continue
						except cx_Oracle.DatabaseError:
							continue
						
						global outputFileCSV
						if outputFileCSV!="":
							for result in results:
								print str(result)
								#Write all results to output file
								fo = open(outputFileCSV, "a+")
								fo.write(str(result)+"\n")
								fo.close()					
						else:
							for result in results:
								print result
						results = curs4.fetchall()
						for searchStr in ccRegex:
							#Credit Card Regex Search
							p = re.compile(searchStr)
							for row_data in results:
								for col in row_data:
									if p.match(str(col)):
										#Run the found CC info thru LUHN algorithm to confirm
										n = p.match(str(col))
										if cardLuhnChecksumIsValid(str(col)):
											print colored("[+] Found valid CC: %s in table %s [%s]" % (col, tableName, sid),"red",attrs=['bold'])
										else:
											print "%s is not valid credit card number" % col
										matchedRows.append(row_data)
						#Write rows that matched to csv file				
						if len(matchedRows) > 0:
							csv_file_dest = dbName +  '_' + tableName + ".csv"
							print colored("\n[+] Results for first ten rows have been saved to "+csv_file_dest+".","red",attrs=['bold'])
							outputFile = open(csv_file_dest,'w') 
							output = csv.writer(outputFile, dialect='excel')			
		
							#if printHeader: # add column headers if requested
							cols = []
							for col in curs4.description:
								cols.append(col[0])
							output.writerow(cols)
			
							for rows in matchedRows: # add table rows
								output.writerow(rows)	
							outputFile.close()
						curs4.close()
				curs3.close()
			curs2.close()	
		curs.close()		
	
	except cx_Oracle.DatabaseError as e:
		print e
		tableNames = []
		if "table or view does not exist" in str(e):
	                print colored("\n[!] Account is not a DBA. Please try to use 'ora_priv.py'.","blue",attrs=['bold'])
                        orcl2 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)
                        curs2 = orcl2.cursor()
                        curs2.execute("SELECT table_name FROM user_tables")
                        #curs2.execute("SELECT table_name FROM all_tab_columns WHERE column_name LIKE \'%%\'")
                        for row_data in curs2:
                        	#Iterate per table 
                                if not row_data[0].startswith('BIN$'): # skip recycle bin tables
                                	tableName = row_data[0]
					if tableName not in tableNames:
						tableNames.append(tableName)
			for tableName in tableNames:
				print str(tableName)
				try:
	                                print colored("\n[+] Ransacking table: "+tableName+" in "+sid,"red",attrs=['bold'])
        	                        orcl4 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)
                	                sql4 = "SELECT column_name FROM USER_TAB_COLUMNS WHERE table_name = '"+str(tableName)+"'"
                        	        curs4 = orcl4.cursor()
                                	curs4.execute(sql4)
	                                matchedRows = []
        	                        results = curs4.fetchall()
					#print str(results)
					newResults = str(results).lower()
					global interestingData
					if interestingData == True:
						if "card" in newResults or "credit" in newResults or "bank" in newResults or "passw" in newResults:
							print str(results)
	        		                        orcl5 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)
        	        		                sql5 = "select * from (select * from  " + tableName+") where rownum <="+str(sample)
                	        		        curs5 = orcl4.cursor()
                        	        		curs5.execute(sql5)
	                        	        	matchedRows = []
	        	                	        results = curs5.fetchall()
							for result in results:
								print str(result)
					else:
						print str(results)
	        	                        orcl5 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)
                		                sql5 = "select * from (select * from  " + tableName+") where rownum <="+str(sample)
               	        		        curs5 = orcl4.cursor()
                       	        		curs5.execute(sql5)
                        	        	matchedRows = []
        	                	        results = curs5.fetchall()
						for result in results:
							print str(result)

				except cx_Oracle.DatabaseError as e:
					if "table or view does not exist" in str(e):
						pass
			#for result in results:
			#	print str(result)
	#	print "cx_Oracle.DatabaseError"
	#	pass	


#outputFileCSV="output4.csv"	
interestingData=False

if __name__=="__main__":
        parser = argparse.ArgumentParser(description='Oracle Privilege Escalation')
        parser.add_argument('-host', help='IP or host name of Oracle server')
        parser.add_argument('-hostFile', dest='hostFile', help='File containing IP addresses of oracle servers')
        parser.add_argument('-u', dest='username', help='Use this username to authenticate')
        parser.add_argument('-p', dest='password', help='Use this password to authenticate')
        parser.add_argument('-sid', dest='sid', help='Use this sid')
        parser.add_argument('-sample', dest='sample', help='Sample size')
        parser.add_argument('-idf', action='store_true', help='Interesting Data Finder')
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

	if args['sample']!=None:
		sample = args['sample']

	if args['idf']:
		interestingData=True

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
			if args['sample']==None:
				sample=5
			dataExtract(username,password,hostname,sid,sample)
