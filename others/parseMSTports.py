#! /usr/bin/env python
# Sachin Agarwal, Google, Twitter: sachinkagarwal, Web: http://sites.google.com/site/sachinkagarwal/ 
# November 2010
# Using Python to execute a bunch of job strings on multiple processors and print out the results of the jobs in the order they were listed in the job list (e.g. serially).
# Partly adapted from http://jeetworks.org/node/81


#These are needed by the multiprocessing scheduler
from multiprocessing import Queue
import multiprocessing
import commands
import sys
import sys
import commands,os
import nmap
import subprocess
import argparse
resultsEnd = []

#These are specific to my jobs requirement
import os
import re

httpList = []
sslList = []
snmpList = []
sshList = []
scanTCPList = []
scanUDPList = []
filename = ''

file = open("results.txt", "w")

def generateCommands():
	print "Generating nmap commands"
	filename = str(sys.argv[1])
	with open(filename) as f:
	        for line in f:
        	        hostNo = line.split(":")[0]
        	        inputStr = line.split(":")[1]
               		inputList = inputStr.split(" ")
                	tcpList=[]
        	        udpList=[]
	                #print "\n"
        	        file.write("\n"+hostNo+"\n")
        	        for i in inputList:
                	        if '/tcp' in i or '/TCP' in i:
                       	        	tmpStr = i.replace('/tcp','')
	                                tmpStr = tmpStr.replace('/TCP','')
       		                        tmpStr = (tmpStr.replace(',','')).replace(" ","").replace("\n","")
                   		  	tcpList.append(tmpStr)
                        	if '/udp' in i or '/UDP' in i:
                                	tmpStr = i.replace('/udp','')
                                	tmpStr = tmpStr.replace('/UDP','')
                                	tmpStr = (tmpStr.replace(',','')).replace(" ","").replace("\n","")
                                	udpList.append(tmpStr)

                	tcpportNo = str(tcpList).strip('[]').replace("'","").replace(" ","")
	                udpportNo = str(udpList).strip('[]').replace("'","").replace(" ","")
                	if len(tcpportNo)>0 and len(udpportNo)>0:
                        	arg = "sudo nmap -Pn -T4 -sT -sU -n -sV  -A  -v --open --script default -p T:"+tcpportNo+" U:"+udpportNo
                        	cmd = arg+" "+hostNo
		        	scanTCPList.append((hostNo,cmd))
                	if len(tcpportNo)>0 and len(udpportNo)<1:
                        	arg = "sudo nmap -Pn -T4 -sT -sU -n -sV  -A  -v --open --script default -p T:"+tcpportNo
                        	cmd = arg+" "+hostNo
		        	scanTCPList.append((hostNo,cmd))
                	if len(tcpportNo)<1 and len(udpportNo)>0:
                        	arg = "sudo nmap -Pn -T4 -sT -sU -n -sV  -A  -v --open --script default -p U:"+udpportNo
                        	cmd = arg+" "+hostNo
		        	scanTCPList.append((hostNo,cmd))


def RunCommand (fullCmd):
    try:
	print fullCmd
        return commands.getoutput(fullCmd)
    except:
        return "Error executing command %s" %(fullCmd)

        
class Worker(multiprocessing.Process):
 
    def __init__(self,
            work_queue,
            result_queue,
          ):
        # base class initialization
        multiprocessing.Process.__init__(self)
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.kill_received = False
 
    def run(self):
        while (not (self.kill_received)) and (self.work_queue.empty()==False):
            try:
                job = self.work_queue.get_nowait()
            except:
                break

            (jobid,runCmd) = job
            rtnVal = (jobid,RunCommand(runCmd))
            self.result_queue.put(rtnVal)

def extractPorts(results):
	file = open("results.txt", "a+")
	resultList = str(results).split("\n")
      	for i in resultList:
		if "Nmap scan report for " in i:
			hostNo = i.replace("Nmap scan report for ","")
 	              	file.write(hostNo+"\n")
        	if "/tcp" in i and "unknown" not in i and "tcpwrapped" not in i and "port" not in i:
                      	outputStr = str(i).replace(" open "," ")
                       	outputStr = outputStr.replace("?"," ")
                     	resultsEnd.append(outputStr)
 	              	file.write(outputStr+"\n")

                        if "http" in outputStr:
                        	portStatus = outputStr.split("/tcp")
                              	httpList.append((hostNo,portStatus[0],portStatus[1]))
                      	if "ssl" in outputStr:
                             	portStatus = outputStr.split("/tcp")
                             	sslList.append((hostNo,portStatus[0],portStatus[1]))
                      	if "ssh" in outputStr:
                              	portStatus = outputStr.split("/tcp")
                             	sshList.append((hostNo,portStatus[0],portStatus[1]))

             	if "/udp" in i and "filtered" not in i and "unknown" not in i and "tcpwrapped" not in i and "port" not in i:
                      	outputStr = str(i).replace(" open "," ")
                     	outputStr = outputStr.replace("open|filtered","")
                     	outputStr = outputStr.replace("?"," ")
                     	resultsEnd.append(outputStr)
                     	file.write(outputStr+"\n")
              
 	             	if "snmp" in outputStr:
                        	portStatus = outputStr.split("/udp")
                             	snmpList.append((hostNo,portStatus[0],portStatus[1]))            
	file.close()

def execute(jobs, num_processes=2):
    # load up work queue
    work_queue = multiprocessing.Queue()
    for job in jobs:
        work_queue.put(job)
 
    # create a queue to pass to workers to store the results
    result_queue = multiprocessing.Queue()
 
    # spawn workers
    worker = []
    for i in range(num_processes):
        worker.append(Worker(work_queue, result_queue))
        worker[i].start()
    
    # collect the results from the queue
    results = []
    while len(results) < len(jobs): #Beware - if a job hangs, then the whole program will hang
        result = result_queue.get()
        results.append(result)
    results.sort() # The tuples in result are sorted according to the first element - the jobid
    return (results) 

 
#MAIN 

if __name__ == '__main__':
    global filename
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', help='[file containing directory listing]')
 
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()
    if options.f:
	filename = options.f

    	generateCommands()
    
    	import time #Code to measure time
    	starttime = time.time() #Code to measure time
    
   
    	jobs = [] #List of jobs strings to execute
    	jobid = 0#Ordering of results in the results list returned

    	#Code to generate my job strings. Generate your own, or load joblist into the jobs[] list from a text file
    	lagFactor = 5
    	for i in scanTCPList:
		cmd = i[1]
    		#cmd = "nmap -Pn -T4 -sT -n -sV  -A  -v --open --script default -p 443,8009 58.215.166.36"
    		ctr = 0
    		fullCmd = cmd 	#Linux command to execute
    		jobs.append((jobid,fullCmd)) # Append to joblist
    		jobid = jobid+1
	for i in scanUDPList:
		cmd = i[1]
    		#cmd = "nmap -Pn -T4 -sT -n -sV  -A  -v --open --script default -p 443,8009 58.215.166.36"
    		ctr = 0
    		fullCmd = cmd 	#Linux command to execute
    		jobs.append((jobid,fullCmd)) # Append to joblist
    		jobid = jobid+1    
    	# run
    	numProcesses = 10
    	results = execute(jobs,numProcesses) #job list and number of worker processes
    
    	#Code to print out results as needed by me. Change this to suit your own need
    	# dump results
    	ctr = 0
    	for r in results:
    	    (jobid, cmdop) = r  
    	    #if jobid % lagFactor == 0:
    	    #    print
       	    #    print jobid/lagFactor,
            #print '\t',
            #try:
       	    #print cmdop
	    extractPorts(cmdop)
            #print cmdop.split()[10],
            #except:
            #    print "Err",
            ctr = ctr+1
    	print

    	file1 = open("results_sorted.txt", "w")
    	results1 =  "\n***** HTTP/HTTPs Servers *****"
    	print results1
    	file1.write(results1+"\n")
    	for host in httpList:
    		if "ssl/http" in str(host):
       	        	results1 = "https://"+host[0]+":"+host[1]
			print results1
			file1.write(results1+"\n")
        	if " http " in str(host):
        	        results1 = "http://"+host[0]+":"+host[1]
		print results1
		file1.write(results1+"\n")
    	results1 = "\n***** SSL Servers *****"
    	print results1
    	file1.write(results1+"\n")
    	for host in sslList:
    		results1 = host[0]+":"+host[1]
		print results1
		file1.write(results1+"\n")
    	results1 = "\n***** SNMP Servers *****"
    	print results1
    	file1.write(results1+"\n")
    	for host in snmpList:
        	results1 = host[0]+":"+host[1]
        	print results1
		file1.write(results1+"\n")
    	results1 = "\n***** SSH Servers *****"
    	print results1
    	file1.write(results1+"\n")
    	for host in sshList:
        	results1 = host[0]+":"+host[1]
        	print results1
		file1.write(results1+"\n")
    	file1.close()
	print "Time taken = %f" %(time.time()-starttime) #Code to measure time
