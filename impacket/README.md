Impacket Scripts Mod
============
Please see below for changes to wmiexec.py script
Special thanks for Corelabs for making these scripts.
Impacket scripts can be found here https://code.google.com/p/impacket/.

The use case scenario for these modded scripts is that the password contains special characters like @ or : and you can't use it with the default wmiexec.py/psexec.py/smbexec.py scripts.

These 3 scripts are the common tools to use if you want to get the remote host to execute a meterpreter exe file generated via Veil-Evasion. 

![alt tag](https://raw.githubusercontent.com/milo2012/pentest_scripts/master/impacket/wmiexec.png)
```
python wmiexec.py  -d testdomain -u user -p pass -ip 192.168.2.1 -command ipconfig
or
python wmiexec.py  -d testdomain -u user -p pass -ip 192.168.2.1 -f ips.txt -command ipconfig
```

![alt tag](https://github.com/milo2012/pentest_scripts/raw/master/impacket/smbexec.png)
```
python smbexec.py  -d testdomain -u user -p pass -ip 192.168.2.1 
or
python smbexec.py  -d testdomain -u user -p pass -f ips.txt 
```

![alt tag](https://github.com/milo2012/pentest_scripts/raw/master/impacket/psexec.png)
```
python psexec.py  -d testdomain -u user -p pass -ip 192.168.2.1 -command ipconfig
or 
python psexec.py  -d testdomain -u user -p pass -f ips.txt -command ipconfig
```
