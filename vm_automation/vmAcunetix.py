import multiprocessing
import os
import commands
import glob
import argparse
import sys
import urllib2 

noGUI=False
numProcesses=5
username=''
password=''
filename=''

#Change the below and point to the VMX file of the VM
vmHost='"/VM/XPLiteVM.vmwarevm/XPLiteVM.vmx"'

acunetixCmd = '"C:\Program Files\Acunetix\Web Vulnerability Scanner 9.5\wvs_console.exe"' 
vmrunCmd='"/Applications/VMware Fusion.app/Contents/Library/vmrun"'
cmdList=[]

fileList=[]
mkdirList=[]

def chunk(input, size):
        return map(None, *([iter(input)] * size))


class Worker1(multiprocessing.Process):

    def __init__(self,
            work_queue,
            result_queue,
          ):
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
            (jobid,filename) = job
            rtnVal = (jobid,generateAcunetix(filename))
            self.result_queue.put(rtnVal)

def execute1(jobs, num_processes=2):
    work_queue = multiprocessing.Queue()
    for job in jobs:
        work_queue.put(job)

    result_queue = multiprocessing.Queue()
    worker = []
    for i in range(int(num_processes)):
        worker.append(Worker1(work_queue, result_queue))
        worker[i].start()

    results = []
    while len(results) < len(jobs):
        result = result_queue.get()
        results.append(result)
    results.sort()
    return (results)

def testInternet():
	cmd = "ping -c3 4.2.2.2 > /dev/null 2>&1"
	if os.system(cmd)==0:
		return True
	else:
		print "[!] Internet is down. Please check"
		sys.exit()
		return False

def RunCommand(fullCmd):
    try:
        return commands.getoutput(fullCmd)
    except Exception as e:
	print e
        return "Error executing command %s" %(fullCmd)

def get_redirected_url(url):
    try:
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        request = opener.open(url)
        return request.url
    except Exception as e:
        return None

def checkWorkDone(folderName):
	#print folderName+'/wvs_log*.csv'	
	files = glob.glob(folderName+'/wvs_log*.csv')
	complete=False
	for name in files:
		with open(name) as f:
			textList=f.read()
			for line in textList:
				if "Finish time           :" in line:
				#if "Scan was aborted      : NO" in line:
					completed=True
	if complete==True:
		return True
	else:
		return False

def generateAcunetix(line):
	line1 = (line.replace(":","_")).replace("//","")
	shareName = line1
	folderName = "/results/"+line1
	folderName1 = (folderName.replace("/","\\")).replace("results","")

	#Enable Shared Folders
	cmd = vmrunCmd+' enableSharedFolders '+vmHost
	RunCommand(cmd)	

	if checkWorkDone(os.getcwd()+folderName)==False and testInternet()==True:
		cmd = vmrunCmd+' addSharedFolder '+vmHost+' '+shareName+' '+os.getcwd()+folderName
		print cmd 
		RunCommand(cmd)	

		if noGUI==True:
			cmd = vmrunCmd+' -T fusion -gu '+username+' -gp '+password+' runProgramInGuest '+vmHost+' -interactive '+acunetixCmd+' /save /savefolder z:'+folderName1+' /Scan '+line+" nogui"
			print cmd
			RunCommand(cmd)	
		else:
			cmd = vmrunCmd+' -T fusion -gu '+username+' -gp '+password+' runProgramInGuest '+vmHost+' -interactive '+acunetixCmd+' /save /savefolder z:'+folderName1+' /Scan '+line
			print cmd
			RunCommand(cmd)	

		#Remove Shares in VMware
		cmd = vmrunCmd+' removeSharedFolder '+vmHost+' '+shareName
		RunCommand(cmd)	



if __name__ == '__main__':
    global numProcess
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='username',  action='store', help='[username to use to login into VM]')
    parser.add_argument('-p', dest='password',  action='store', help='[password to use to login into VM]')
    parser.add_argument('-iL', dest='filename',  action='store', help='[text file containing list of URLs]')
    parser.add_argument('-nogui', action='store_true', help='[starts VM with no gui]')
    parser.add_argument('-n', dest='threads',  action='store', help='[number of threads]')

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    options = parser.parse_args()
    if options.username and options.password and options.filename:
	username = options.username
	password = options.password

	if options.threads:
		numProcesses=options.threads
	if options.nogui:
		noGUI=True
	if options.filename:
		filename=options.filename
		fileList.append(filename)

	if testInternet()==False:
		print "[!] Internet is down. Please check"
		sys.exit()

	#Starts VM
	print "- Starts VM"
	cmd = vmrunCmd+' start '+vmHost
	RunCommand(cmd)	

	fileList1=[]
	for filename in fileList:
		with open(filename) as f:
			lines = f.read().splitlines()
			for line in lines:	
				line =  get_redirected_url(line)
				if line!=None:
					line1 = (line.replace(":","_")).replace("//","")
					shareName = line1
					folderName = "/results/"+line1	
	
					if not os.path.exists(os.getcwd()+"/"+folderName+"/scan-results.wvs"):
						fileList1.append(line)               

					#Remove Shares in VMware
					#cmd = vmrunCmd+' removeSharedFolder '+vmHost+' '+shareName
					#RunCommand(cmd)		

					if not os.path.exists(os.getcwd()+"/"+folderName): 
						os.makedirs(os.getcwd()+"/"+folderName)


	print "- Slicing cmdList into chunks"
	tempList = chunk(fileList1, int(numProcesses))
	totalCount=len(tempList)
	count = 1
	for fileList in tempList:
		jobs = []
		jobid=0
		print "- Set "+str(count)+" of "+str(totalCount)
		for filename in fileList:
			if filename!=None:
				print "- Testing: "+filename
				jobs.append((jobid,filename))
				jobid = jobid+1
      		resultsList = execute1(jobs,numProcesses)


