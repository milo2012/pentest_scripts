# -*- coding: utf-8 -*-
import sys
import optparse 

'''
If you received a file/directory listing provided by the customer for a particular website, 
you can use the below script to convert it into something you can use inside burp intruder

├── CHANGELOG.txt
├── COPYRIGHT.txt
├── INSTALL.mysql.txt
├── INSTALL.pgsql.txt
├── INSTALL.sqlite.txt
├── INSTALL.txt
├── LICENSE.txt
├── MAINTAINERS.txt
├── README.txt
├── UPGRADE.txt
├── xxx
│   ├── xxx.patch
│   ├── yyy.patch
'''

parser = optparse.OptionParser()
parser.add_option('-f', action="store", dest="filename")
options, remainder = parser.parse_args()

if not options.filename:
	sys.exit()
else:
	filename=options.filename
	text_file = open(filename, "r")
	lines = text_file.readlines()

	level1="├── "
	level2="│   ├── "
	level3="│   │   ├── "
	level4="│   │   │   ├── "	
	lastLevel=0
	lastLevel1=""
	lastLevel2=""
	lastLevel3=""

	for x in lines:
		if x.startswith(level1):
			x=x.replace(level1,"")
			x=x.strip()
			print "/"+x
			lastLevel1="/"+x
			lastLevel=0
		if x.startswith(level2):
			x=x.replace(level2,"")
			x=x.strip()
			lastLevel2=x
			print lastLevel1+"/"+x
			lastLevel=1
		if x.startswith(level3):
			x=x.replace(level3,"")
			x=x.strip()
			if " ->" in x:
				x=x.split(" ->")[0]
			lastLevel3=x
			print lastLevel1+"/"+lastLevel2+"/"+x
			lastLevel=2
		if x.startswith(level4):
			x=x.replace(level4,"")
			x=x.strip()
			if " ->" in x:
				x=x.split(" ->")[0]
			lastLevel4=x
			print lastLevel1+"/"+lastLevel2+"/"+lastLevel3+"/"+x
			lastLevel=3
		
