###Simple Starting Points ### 


### Global Variables - Remove Hardcoding once interactive!! ###

AMINE1 = 'A1'
AMINE2 = 'A2'
AMINE3 = 'A3'

import json

### Replaces template JSON file with the desired amines ##
def updateJSON():
 Template= json.load(open('PerovskiteRunDataTemplate.json', 'r')) 
#   print(json.dumps(Template, indent=4, sort_keys=True))
 print(Template)

updateJSON()
