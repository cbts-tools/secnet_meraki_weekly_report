# secnet_meraki_weekly_report
 
This script will pull all meraki organization devices and send a weekly report to Amarnath, using CBTS Cloud Networking Bot.

## Environment Variables

- path: /home/cloudnetautomation/pythonscripts/meraki-email-tirediscounters-license/.env
- env variables: 
  * webex_secure_cloudnetworking_bot_token
  * MERAKI_DASHBOARD_API_KEY
  * O365app_id
  * O365secret
  * O365tenant_id
  * VCO33TOKEN



## Email address

- receivers:
  * amarnath.neelameham@cbts.com
- sender:
  * cloudnetautomation@cbts.com

## Webex message

- receivers:
  * "amarnath.neelameham@cbts.com"


## Steps to add the script to rundeck

- on the server:
  * cd /home/cloudnetautomation/pythonscripts/
  * gh  auth login
  * git clone https://github.com/cbts-tools/secnet_meraki_weekly_report.git
  * cd secnet_meraki_weekly_report/
  * git pull origin main
  *
  * python3 -m venv venv_td
  * source venv/bin/activate
  * pip install -r requirements.txt
  * python3 get_all_meraki_devices.py


- on the app:
````
#!/bin/bash
set -x
python3 get_all_meraki_devices.py
sleep 5
deactivate
````