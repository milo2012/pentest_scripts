#!/usr/bin/python
import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', action='store', help='[file containing directory listing]')
 
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()
    if options.f:
	with open(options.f) as f:
    		content = f.readlines()
	fullPath = ''
	for i in content:
		i = i.strip()
		if '/' in i:
			fullPath = i.replace(":","")
		elif "total " in i or len(i)<1:
			continue
		else:
			pathSplit = i.split(" ")
			try:
				if len(pathSplit)<12:
					print fullPath+"/"+pathSplit[10]
			except IndexError:
				continue
