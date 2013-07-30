#!/usr/bin/python
# -*- coding: utf-8 -*-

import email,os,imaplib
from imapclient import IMAPClient
from email.utils import parseaddr
import socket,sys,time
import multiprocessing
import getpass, poplib
import socket

imapserver = ''
popserver = ''
verbose=False
SSL=True
SEARCH=False
USERNAME = ''
PASSWORD = ''
INPUTFILE = ''
emails_dir = os.getcwd()+"/result/"


def isOpen(ip,port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	try:
		s.settimeout(1)
   		s.connect((ip, int(port)))
     		s.close()
     		return True
    	except:
     		return False

def fetch_email(server,msgid,username):
	if not os.path.exists(emails_dir+"attachments/"+username):
		os.makedirs(emails_dir+"attachments/"+username)

	response = server.fetch(msgid, ['RFC822'])
    	for msgid, data in response.iteritems():
        	msg_string = data['RFC822']
		msg = email.message_from_string(msg_string)
		if msg.get_content_maintype() == 'multipart':
			for part in msg.walk():
				filename = part.get_filename()
				if filename:
	        	        	msgbody = (part.get_payload(decode=True))
					if msgbody!=None:
			                     	att_path = os.path.join(emails_dir+"attachments/"+username+"/", filename)
        		                      	if not os.path.exists(att_path):
                		               		print "[+] Saving attachments: "+att_path
                       			               	fp = open(att_path, 'wb')
                               		        	fp.write(msgbody)
                                		       	fp.close()
						else:
							if verbose==True:
								print "[-] Skipping "+att_path


		if msg.get_content_maintype() != 'multipart':
        		continue
	    	for part in msg.walk():
			msgbody = ""
			#print 'Content-Type:',part.get_content_type()
 			#print 'Main Content:',part.get_content_maintype()
 			#print 'Sub Content:',part.get_content_subtype()

  			if part.get_content_maintype() == 'multipart':
    				continue
			if part.get_content_subtype() == 'plain':
        	                msgbody = part.get_payload(decode=True)        	        			
				return msgbody
			if part.get_content_subtype() == 'html':
        	                msgbody = part.get_payload(decode=True)        	        			
				return msgbody

			#if part.get_content_maintype() == 'multipart':			
			#	continue
			if part.get('Content-Disposition') is None:
				continue
			#else:
			#	print part.get_content_maintype()
	                #	msgbody = (part.get_payload(decode=True))
			#	print msgbody			


			"""
			"""
def connectMailboxPOP(username,password,popserver,SSL):
	print "[*] Accessing: "+popserver+" - "+username

       	emailPath = emails_dir+"emails/"+username+"/Inbox"
      	if not os.path.exists(emailPath):
       		os.makedirs(emailPath)
	HOST = popserver
	ssl = SSL
	if SSL==True:
	        Mailbox = poplib.POP3_SSL(popserver, '995')
	else:
	        Mailbox = poplib.POP3(popserver, '110')
	Mailbox.user(username)
	Mailbox.pass_(password)

	numMessages = len(Mailbox.list()[1])
	progressBar = False
	print "[+] Downloading: "+str(numMessages)+" email(s) - "+username

	for i in range(numMessages):
        	response = Mailbox.retr(numMessages+1-(i+1))
        	#response = Mailbox.retr(numMessages+1-(i+1))
        	#response = Mailbox.retr(i+1)
        	lines = response[1]
        	emailMessage = email.message_from_string('\n'.join(lines))

        	for part in emailMessage.walk():
	                if part.get_content_maintype() == 'text':
        	                msgbody = part.get_payload(decode=True)        	        			
                   	   	att_path = os.path.join(emailPath, str(i+1))
	                       	if not os.path.exists(att_path):
					#Write emails to local drive
					if len(msgbody)>0:
						if verbose==True:
							print "[+] Saving emails: "+att_path+" of "+str(numMessages)+" emails"
	       		               			fp = open(att_path, 'wb')
       			       				fp.write(msgbody)
       			        			fp.close()
				else:
					if verbose==True:
						print "[-] Skipping "+att_path+" of "+str(numMessages)+" emails"
				if progressBar==True:
					print "\n"

			if part.get_content_maintype() == 'multipart':
               			continue
               		if part.get('Content-Disposition') is None:
               		        continue
               		filename = part.get_filename()
			if (filename):
				if not os.path.exists(emails_dir+"attachments/"+username):
					os.makedirs(emails_dir+"attachments/"+username)

	                	msgbody = (part.get_payload(decode=True))
				if msgbody!=None:
		                     	att_path = os.path.join(emails_dir+"attachments/"+username+"/", filename)
        	                      	if not os.path.exists(att_path):
                	               		print "[+] Saving attachments: "+att_path
                       		               	fp = open(att_path, 'wb')
                               	        	fp.write(msgbody)
                                	       	fp.close()
					else:
						if verbose==True:
							print "[-] Skipping "+att_path
			if not (filename): continue


def connectMailboxIMAP(username,password,imapserver,SSL):
	print "[*] Accessing: "+imapserver+" - "+username
	HOST = imapserver
	ssl = SSL
	mail = imaplib.IMAP4_SSL(HOST)
	mail.login(username,password)

	server = IMAPClient(HOST, use_uid=True, ssl=ssl)
	server.login(username,password)
	folders = server.list_folders()
		
	for folder in folders:
		#try:
			emailPath = emails_dir+"emails/"+username+"/"+folder[2]
			if not os.path.exists(emailPath):
				os.makedirs(emailPath)
		
      	 	      	server.select_folder(folder[2])
      		        messages = server.search(['NOT DELETED'])

			progressBar = False
			print "[+] Downloading from '"+str(folder[2]).strip()+"' folder: "+str(len(messages))+" email(s) - "+username
			for msg in messages:
				#print msg
				#msgid = str(msg).strip("L")
				
				#Fetch email from server if email is not downloaded yet
				att_path = os.path.join(emailPath, str(msg))

				if not os.path.exists(att_path):
					msgbody=fetch_email(server,msg,username)								
					#Write emails to local drive
					if msgbody!=None and len(msgbody)>0:
						if verbose==True:
							print "[+] Saving emails: "+att_path 
	       		               		fp = open(att_path, 'wb')
       			       		       	fp.write(msgbody)
       			        	        fp.close()

						#if(len(messages)>10):
						#	progressBar = True
						#	sys.stdout.write('.')
						#	sys.stdout.flush()
				else:
					if verbose==True:
						print "[-] Skipping "+att_path
			if progressBar==True:
				print "\n"
		#except:
		#	continue
	

def checkEmailServer():
	jobs = []
	accounts = []
	
	if(len(USERNAME)>0 or len(PASSWORD)>0):
        	uname,domain = USERNAME.split('@')
               	print "[*] Checking: "+USERNAME
	
		emailServer = ''
		if isOpen('pop.'+domain,995):
			popserver = 'pop.'+domain
			emailServer = 'pop'
			SSL=True
		if isOpen('pop.'+domain,110):
			popserver = 'pop.'+domain
			emailServer = 'pop'
			SSL=False
		if isOpen('pop3.'+domain,995):
			popserver = 'pop3.'+domain
			emailServer = 'pop'
			SSL=True
		if isOpen('pop3.'+domain,110):
			popserver = 'pop3.'+domain
			emailServer = 'pop'
			SSL=False
		if isOpen('imap.'+domain,465):
			imapserver = 'imap.'+domain
			emailServer = 'imap'
			SSL=True
		if isOpen('imap.'+domain,143):
			imapserver = 'imap.'+domain
			emailServer = 'imap'
			SSL=False
			
		if emailServer=='pop':
        		       	p = multiprocessing.Process(
               		        	target=connectMailboxPOP,
                	      		args=(USERNAME,PASSWORD,popserver,SSL,)
                	        )
                	        jobs.append(p)
                       		p.start()
		if emailServer=='imap':
        		       	p = multiprocessing.Process(
        	       		       	target=connectMailboxIMAP,
                	       		args=(USERNAME,PASSWORD,imapserver,SSL,)
                	        )
                       		jobs.append(p)
                        	p.start()


	if(len(INPUTFILE)>0):	
		with open(INPUTFILE) as f:
		        accounts = f.readlines()
		for account in accounts:
		        account = account.strip()
		        if len(account)>0:
        		        username,password = account.split()
               			uname,domain = username.split('@')

               		 	print "[*] Checking: "+username

				emailServer = ''
				if isOpen('pop.'+domain,995):
					popserver = 'pop.'+domain
					emailServer = 'pop'
					SSL=True
				if isOpen('pop.'+domain,110):
					popserver = 'pop.'+domain
					emailServer = 'pop'
					SSL=False
				if isOpen('pop3.'+domain,995):
					popserver = 'pop3.'+domain
					emailServer = 'pop'
					SSL=True
				if isOpen('pop3.'+domain,110):
					popserver = 'pop3.'+domain
					emailServer = 'pop'
					SSL=False
				if isOpen('imap.'+domain,465):
					imapserver = 'imap.'+domain
					emailServer = 'imap'
					SSL=True
				if isOpen('imap.'+domain,143):
					imapserver = 'imap.'+domain
					emailServer = 'imap'
					SSL=False

				if emailServer=='pop':
        			       	p = multiprocessing.Process(
               			        	target=connectMailboxPOP,
                		      		args=(username,password,popserver,SSL,)
                		        )
                		        jobs.append(p)
                	       		p.start()

				if emailServer=='imap':
        			       	p = multiprocessing.Process(
        	       			       	target=connectMailboxIMAP,
                		       		args=(username,password,imapserver,SSL,)
                		        )
                       			jobs.append(p)
                        		p.start()

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(__file__)
	parser = argparse.ArgumentParser(description="Emails are saved to [current-dir]/result/emails/[email-address] folder. Attachments are saved to [current-dir]/result/attachments/[email-address] folder.")
	parser.add_argument('-u','--user', help='Email address', required=False)
	parser.add_argument('-p','--pass', help='Email account password', required=False)
	parser.add_argument('-f','--file', help='File containing list of email accounts', required=False)
	parser.add_argument('-d','--dest', help='Location to save downloaded emails', required=False)
	#parser.add_argument('-s','--search', help='Search emails for passwords and credit cards', action='store_true')	
	parser.add_argument('-v','--verbose', help='Enable verbose mode', action='store_true')	
	args = vars(parser.parse_args())
	
	#if args['search']!=None:
	#	SEARCH = True
	#	if SEARCH==True:
	#		for text in searchText:
	#			searchthis(emails_dir, text)
	if args['verbose']:
		verbose=True
	if args['dest']!=None:	
		emails_dir = args['dest']+"/emails/"
		if not os.path.exists(emails_dir):
        		os.makedirs(emails_dir)
 	if args['user']!=None and args['pass']!=None:
		USERNAME = args['user']
		PASSWORD = args['pass']
		checkEmailServer()
	if args['file']!=None:
		INPUTFILE = args['file']
		checkEmailServer()
		
