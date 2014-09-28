CloudFlareSync
==============

This script fetches your records from domain records from cloudflare into a csv file, and then any changes you make to that file can be synced back to cloudflare.

Usage
-------
*python3 cloudflaresync.py [-h] [-fetch] [-sync]*

Before running make sure to rename config.default.json to config.json

**-fetch**

will fetch current records from cloudflare and write it to a local csv file (overwriting existing file). Filename is picked from config.json

**-sync**

will sync will compare the local file with cloudflare records and sync any additions, updates or deletion done in the local file.


Config
--------
Rename config.default.json to config.json

Sample :

    {"file": "records.csv",
    "backup_file": "cf_bkp.csv",
    "url": "https://www.cloudflare.com/api_json.html",
    "email": "your_cloudlfare_email_here",
    "tkn": "your_cloudflare_api_key_here",
    "domains": ["domain1.com", "domain2.com"]}

**file** :          the csv file used to fetch and sync

**backup_file**:    the csv file in which backup of cloudflare records will be stored before sync

**url**:            cloudflare api url, you need not change this until cloudflare changes its api url.

**email**:          email registered with cloudflare

**tkn**:            your cloudflare api key , you can get it from https://www.cloudflare.com/my-account.html

**domains**: the domains to fetch and sync, add all domains you want to fetch and / or sync here

CSV File
----------
Each row in the CSV file indicates a DNS record, the columns are as follows:


**zone_name**  
The target domain

**type**  
Type of DNS record. Values include: [A/CNAME/MX/TXT/SPF/AAAA/NS/SRV/LOC]

**name**  
Name of the DNS record.

**content**  
The content of the DNS record, will depend on the the type of record being added

**ttl**  
TTL of record in seconds. 1 = Automatic, otherwise, value must in between 120 and 86400 seconds.

**prio**[applies to MX/SRV]  
MX record priority.

**service**[applies to SRV]  
Service for SRV record

**srvname**[applies to SRV]  
Service Name for SRV record

**protocol**[applies to SRV]  
Protocol for SRV record. Values include: [_tcp/_udp/_tls].

**weight**[applies to SRV]  
Weight for SRV record.

**port**[applies to SRV]  
Port for SRV record

**target**[applies to SRV]  
Target for SRV record

**rec_id**  
Cloudflare record id, it is used to update the correct record. if you are adding a new record, leave it blank




Editing the CSV File
---------------------

*Deleting a row from the csv will delete the record*

*Changing any values in a existing record in the csv will update the corresponding record on cloudflare (based on rec_id column)*

*To add a record simply add the details needed for that type and the script will add it to cloudflare, run fetch again to get the rec_id for this record too*
