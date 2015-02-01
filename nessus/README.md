sudo python nmap2ness.py -h
usage: nmap2ness.py [-h] [-s HOSTIP] [-n SCANID] [-u USERNAME] [-p PASSWORD]
                    [-i INFILE] [-o OUTFILE]
```
optional arguments:
  -h, --help   show this help message and exit
  -s HOSTIP    [nessus server IP]
  -n SCANID    [lookup job based on scan_id]
  -u USERNAME  [username]
  -p PASSWORD  [password]
  -i INFILE    [nmap xml file]
  -o OUTFILE   [nessus report (csv)]
```  
    
sudo python nmap2ness.py -u root -p 1234 -i nmapt_target.xml -s 127.0.0.1  
```
- Launching new Nessus scan
- Extracting ports from nmapt_target.xml
- Modifying Nessus policy
- Logging into Nessus
- Uploading Policy
- Starting Nessus Scan
- Checking Job Status: 224 : running
- Checking Job Status: 224 : running
- Checking Job Status: 224 : running
- Checking Job Status: 224 : running
- Checking Job Status: 224 : running
- Checking Job Status: 224 : running
- Checking Job Status: 224 : paused
- Checking Job Status: 224 : paused
- Checking Job Status: 224 : paused
- Checking Job Status: 224 : paused
- Checking Job Status: 224 : paused
- Checking Job Status: 224 : canceled
- Nessus report has been saved to: report.csv
```
