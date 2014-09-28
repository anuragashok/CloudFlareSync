CloudFlareSync
==============

This script fetches your records from domain records from cloudflare into a csv file, and then any changes you make to that file can be synced back to cloudflare.

Usage
-------
*python3 cloudflaresync.py [-h] [-fetch] [-sync]*

Before running make sure to rename config.default.json to config.json

**-fetch **

will fetch current records from cloudflare and write it to a local csv file (overwriting existing file). Filename is picked from config.json

**-sync **

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
