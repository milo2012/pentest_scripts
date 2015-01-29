- vmAcunetix.py  

Starts up the VM (background optional with the -nogui parameter to improve performance)  
Launches Acunetix and scans the URLs listed in the text files.
 ``` 
usage: vmAcunetix.py [-h] [-u USERNAME] [-p PASSWORD] [-iL FILENAME] [-nogui]
                     [-n THREADS]

optional arguments:
  -h, --help    show this help message and exit
  -u USERNAME   [username to use to login into VM]
  -p PASSWORD   [password to use to login into VM]
  -iL FILENAME  [text file containing list of URLs]
  -nogui        [starts VM with no gui]
  -n THREADS    [number of threads]
```
