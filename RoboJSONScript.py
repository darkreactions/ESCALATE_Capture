from time import gmtime, strftime
import json
from oauth2client.service_account import ServiceAccountCredentials
import Google_IO
import gspread
import argparse as ap

##########################################################
#  _        ___           _                              #
# |_)    o   |   _. ._   |_) _  ._   _| |  _ _|_  _  ._  #
# |_) \/ o  _|_ (_| | |  |  (/_ | | (_| | (/_ |_ (_) | | #
#     /                                                  #
##########################################################

### Command line parsing for taking data from shell script
### This will need some work to generalize the argparse input

parser = ap.ArgumentParser(description='Required Input Amine1 Amine2 Amine3, other values have default options')
parser.add_argument('amine1', metavar='A1', type=str, help='amine used in the first stock solution')
parser.add_argument('amine2', metavar='A2', type=str, help='amine used in the second stock solution')
parser.add_argument('amine3', metavar='A3', type=str, help='amine used in the third stock solution')
parser.add_argument('VS', type=float, help='')
parser.add_argument('Temp1', type=int, help='')
parser.add_argument('S1RPM', type=int, help='')
parser.add_argument('S1Dur', type=int, help='')
parser.add_argument('S2RPM', type=int, help='')
parser.add_argument('S2Dur', type=int, help='')
parser.add_argument('Temp2', type=int, help='')
parser.add_argument('FinalHold', type=int, help='')
args = parser.parse_args()


### Simple Starting Points ### 
### Importing some variables from argparse ####
AMINE1 = args.amine1
AMINE2 = args.amine2
AMINE3 = args.amine3
VS = args.VS
Temp1 = args.Temp1
S1RPM = args.S1RPM
S1Dur = args.S1Dur
S2RPM = args.S2RPM
S2Dur = args.S2Dur
Temp2 = args.Temp2
FinalHold = args.FinalHold
lab = 'LBL'
Creator = "Ian"

##Setup Run ID Information
readdate=strftime("%Y-%m-%d")
date=strftime("%Y%m%d")
time=strftime("%H%M%S")
readtime=strftime("%H:%M:%S")
RunID=date + "_" + time + "_" + lab + "_" + Creator #Agreed Upon format for final run information
print("Date: %s Time: %s" %(readdate,readtime))  #Agreed Upon format for final run information

##Generates new working directory with updated templates, return working folder ID
def NewWrkDir(RunID): 
    NewDir=Google_IO.DriveCreateFolder(RunID)
    file_dict=Google_IO.DriveAddTemplates(NewDir, RunID)
    return(file_dict) #returns the experimental data sheet google pointer url (GoogleID)

##Open, read and print some information from the google sheet template ##
def ReadSheet(ExpDataFormKey):
    scope= ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    gc =gspread.authorize(credentials)
    testsheet = gc.open_by_key(ExpDataFormKey).sheet1
    return(testsheet) #returns the experimental data entry gspread object

##Updates all of the run data information and creates the empty template for amine information
def PrepareDirectory(RunID):
    new_dict=NewWrkDir(RunID)
    for key,val in new_dict.items():
        if "ExpDataEntry" in key:
            sheetobject=ReadSheet(val)
        elif "RobotInput" in key:
            print(Google_IO.GDLFile(key, val))
    sheetobject.update_cell(2,2, readdate) #row, column, replacement in experimental data entry form
    sheetobject.update_cell(3,2, readtime)
    sheetobject.update_cell(4,2, lab)
    sheetobject.update_cell(6,2, RunID)
    sheetobject.update_cell(17,3, AMINE1)
    sheetobject.update_cell(21,3, AMINE2)
    sheetobject.update_cell(25,3, AMINE3)
    sheetobject.update_cell(7,2, VS)
    sheetobject.update_cell(2,4, Temp1)
    sheetobject.update_cell(4,4, S1RPM)
    sheetobject.update_cell(4,7, S1Dur)
    sheetobject.update_cell(6,4, S2RPM)
    sheetobject.update_cell(6,7, S2Dur)
    sheetobject.update_cell(7,4, Temp2)
    sheetobject.update_cell(8,7, FinalHold)
    print('done')

PrepareDirectory(RunID)
