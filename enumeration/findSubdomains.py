import  optparse
import sys
import requests
import json

tmpDomainList=[]

def lookup(domainName):
	nextLink=''
	url='https://transparencyreport.google.com/transparencyreport/api/v3/httpsreport/ct/certsearch?include_expired=true&include_subdomains=true&domain='+domainName
	content = requests.get(url)
	lines=(content.text).split("\n")
	contentStr=""
	for x in lines:
		x=x.strip()
		if x!=")]}'":	
			contentStr+=x

	data = json.loads(contentStr)
	x=0
	while x<len((data[0][1])):
		foundDomain=data[0][1][x][1]
		if foundDomain not in tmpDomainList:
			print foundDomain
			tmpDomainList.append(foundDomain)
		x+=1
	nextLink=data[0][3][1]
	return nextLink
def lookupNextPage(tmpLink):
	url='https://transparencyreport.google.com/transparencyreport/api/v3/httpsreport/ct/certsearch/page?p='+tmpLink
	content = requests.get(url)
	lines=(content.text).split("\n")
	contentStr=""
	for x in lines:
		x=x.strip()
		if x!=")]}'":	
			contentStr+=x

	data = json.loads(contentStr)
	x=0
	while x<len((data[0][1])):
		foundDomain=data[0][1][x][1]
		if foundDomain not in tmpDomainList:
			print foundDomain
			tmpDomainList.append(foundDomain)
		x+=1
	nextLink=data[0][3][1]
	return nextLink

parser = optparse.OptionParser()
parser.add_option('-d', action="store", dest="domainName")
options, remainder = parser.parse_args()
if options.domainName:
	domainName=options.domainName
	nextLink=lookup(domainName)
	try:
		while len(nextLink)>0:
			if len(nextLink)>0:
				nextLink=lookupNextPage(nextLink)
	except TypeError:
		pass
		
else:
	print "[!] Please provide a domain name using the -d argument"
	sys.exit()
