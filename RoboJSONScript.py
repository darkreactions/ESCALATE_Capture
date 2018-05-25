from time import gmtime, strftime
import json
import Google_IO


###Simple Starting Points ### 
### Global Variables - Remove Hardcoding once interactive!! ###
AMINE1 = 'A1'
AMINE2 = 'A2'
AMINE3 = 'A3'

##Setup Run ID Information
date=strftime("%Y%m%d_%H%M%S")
lab="LBL"
RunID=date + "_" + lab

### Replaces template JSON file with the desired amines ##
def updateJSON():
 Template= json.load(open('PerovskiteRunDataTemplate.json', 'r')) 
#   print(json.dumps(Template, indent=4, sort_keys=True))
 print(Template)

Google_IO.DriveCreateFolder(RunID)