#Credits to:  
(1) cirt.net - For providing the extensive database of default credentials.

#Below are examples of how you can use the generated wordlists
```
medusa -M ssh -C wordList_ssh.txt -H port22_hosts.txt
medusa -M telnet -C wordList_telnet.txt -H port23_hosts.txt 
patator.py ssh_login host=10.0.0.1 user=FILE0 password=FILE1 0=users.txt 1=passwords.txt -x ignore:mesg='Authentication failed.'
```

