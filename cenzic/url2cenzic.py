import urllib2
import socket
import argparse
import sys
import multiprocessing

numProcess=10
default_timeout = 10
socket.setdefaulttimeout(default_timeout)

def get_redirected_url(url):
    try:
    	opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	urllib2.install_opener(opener)
	request = opener.open(url)
    	return request.url
    #except urllib2.HTTPError:
    #	return None
    #except urllib2.URLError:
    #	return None
    except Exception as e:
	#return str(e)
	return None


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

            (jobid,url) = job
            rtnVal = (jobid,get_redirected_url(url))
            self.result_queue.put(rtnVal)

def execute(jobs, num_processes=2):
    # load up work queue
    work_queue = multiprocessing.Queue()
    for job in jobs:
        work_queue.put(job)

    # create a queue to pass to workers to store the results
    result_queue = multiprocessing.Queue()

    # spawn workers
    worker = []
    for i in range(int(num_processes)):
        worker.append(Worker(work_queue, result_queue))
        worker[i].start()

    # collect the results from the queue
    results = []
    while len(results) < len(jobs): #Beware - if a job hangs, then the whole program will hang
        result = result_queue.get()
        results.append(result)
    results.sort() # The tuples in result are sorted according to the first element - the jobid
    return (results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='filename', action='store', help='[filename containing urls]')
    parser.add_argument('-p', dest='projectName', action='store', help='[abbreviation of the project. do not use spaces]')
    parser.add_argument('-o', dest='output', action='store', help='[output cenzic CSV file]')
    options = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    else:
	if not options.output:
		print "[!] Please use the -output argument."
	if not options.filename:
		print "[!] Please use the -filename argument."
  	if options.filename and options.output and options.projectName:
 		resultList=[]
		filename = options.filename
		lines=[]
		with open(filename) as filename:
		    	lines = filename.read().splitlines()
		jobs=[]
		jobid=0
		for line in lines:
			line=line.strip()
			print line	
			if "#" not in line and len(line)>0:
				jobs.append((jobid,line))
				jobid = jobid+1
		results = execute(jobs,int(numProcess))
		for result in results:
			if result[1] not in resultList and result[1]!=None:
				if ['"'+result[1]+'"','"'+options.projectName+"_"+result[1]+'"',"","","","",'"NetPenScan"','"10/2/2014"'] not in resultList:
					resultList.append(['"'+result[1]+'"','"'+options.projectName+"_"+result[1]+'"',"","","","",'"NetPenScan"','"10/2/2014"'])
					#resultList.append(['"'+result[1]+'"','"'+options.projectName+"_"+result[1]+'"',"","","","","",'"NetPenScan"','"10/2/2014"'])
		if len(resultList)>0:
			print "\n\n************** Results **************"
			print "Found the below URLs"
			
			for x in resultList:
				print x[0]

			if ".csv" not in options.output:
				file = open(options.output+".csv", "w")
				for x in resultList:
					file.write(x[0]+','+x[1]+','+x[2]+','+x[3]+','+x[4]+','+x[5]+','+x[6]+','+x[7]+'\n')
				file.close()
				print "[*] Import "+options.output+".csv into Cenzic"
			else:
				file = open(options.output, "w")
				for x in resultList:
					file.write(x[0]+','+x[1]+','+x[2]+','+x[3]+','+x[4]+','+x[5]+','+x[6]+','+x[7]+','+'\n')
				file.close()
				print "[*] Import "+options.output+" into Cenzic"

		else:
			print "\n\n************** Results **************"
			print "- No URLs found"		
