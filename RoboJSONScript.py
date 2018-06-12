from time import gmtime, strftime
import json
from oauth2client.service_account import ServiceAccountCredentials
#import Google_IO
import gspread
import argparse as ap
import pandas as pd

#import matplotlib.pyplot as plt
import optunity
import random


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
#parser.add_argument('amine3', metavar='A3', type=str, help='amine used in the third stock solution')
parser.add_argument('VS', type=float, help='')
parser.add_argument('Temp1', type=int, help='')
parser.add_argument('SRPM', type=int, help='')
parser.add_argument('S1Dur', type=int, help='')
parser.add_argument('S2Dur', type=int, help='')
parser.add_argument('Temp2', type=int, help='')
parser.add_argument('FinalHold', type=int, help='')
parser.add_argument('Debugging', default=1, type=int, help='')
args = parser.parse_args()


### Simple Starting Points ### 
### Importing some variables from argparse ####
AMINE1 = args.amine1
AMINE2 = args.amine2
#AMINE3 = args.amine3
VS = args.VS
Temp1 = args.Temp1
SRPM = args.SRPM
S1Dur = args.S1Dur
S2Dur = args.S2Dur
Temp2 = args.Temp2
FinalHold = args.FinalHold
Debug = args.Debugging #Prevents editing the working directory and provides a dev mode as default
lab = 'LBL'
Creator = "Ian"

##Setup Run ID Information
readdate=strftime("%Y%m%d")
date=strftime("%Y%m%d")
time=strftime("%H%M%S")
readtime=strftime("%H%M%S")
RunID=date + "_" + time + "_" + lab + "_" + Creator #Agreed Upon format for final run information
print("Date: %s Time: %s" %(readdate,readtime))  #Agreed Upon format for final run information

##Generates new working directory with updated templates, return working folder ID
def NewWrkDir(RunID, Debug): 
    NewDir=Google_IO.DriveCreateFolder(RunID, Debug)
    file_dict=Google_IO.DriveAddTemplates(NewDir, RunID, Debug)
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
    new_dict=NewWrkDir(RunID, Debug) #Calls NewWrkDir Function to get the list of files
    for key,val in new_dict.items(): 
        if "ExpDataEntry" in key: #searches for ExpDataEntry Form to get id
            sheetobject=ReadSheet(val)
        elif "RobotInput" in key:  ## Searches for  Robot input to feed to excel manipulation
            print(Google_IO.GDLFile(key, val))
    sheetobject.update_cell(2,2, readdate) #row, column, replacement in experimental data entry form
    sheetobject.update_cell(3,2, readtime)
    sheetobject.update_cell(4,2, lab)
    sheetobject.update_cell(6,2, RunID)
    sheetobject.update_cell(17,3, AMINE1)
    sheetobject.update_cell(21,3, AMINE2)
#    sheetobject.update_cell(25,3, AMINE3)
    sheetobject.update_cell(7,2, VS)
    sheetobject.update_cell(2,4, Temp1)
    sheetobject.update_cell(3,4, Temp2)
    sheetobject.update_cell(5,4, SRPM)
    sheetobject.update_cell(5,7, S1Dur)
    sheetobject.update_cell(7,4, SRPM)
    sheetobject.update_cell(7,7, S2Dur)
    sheetobject.update_cell(8,7, FinalHold)
    print('done')

def CreateRobotXLS():
    outframe=pd.DataFrame()
    rdf=SobolReagent()
#    df=pd.read_excel('20180607_042249_LBL_Ian_RobotInput.xls', sheet_name='NIMBUS_reaction',usecols=(0))
#    df_vial=pd.read_excel('20180607_042249_LBL_Ian_RobotInput.xls', sheet_name='NIMBUS_reaction',usecols=(0))
#    df_r=pd.read_excel('20180607_042249_LBL_Ian_RobotInput.xls', sheet_name='NIMBUS_reaction',usecols=(1,2,3,4,5,6))
#    df_LID=pd.read_excel('20180607_042249_LBL_Ian_RobotInput.xls', sheet_name='NIMBUS_reaction',usecols=(7))
#    df_Reagent=pd.read_excel('20180607_042249_LBL_Ian_RobotInput.xls', sheet_name='NIMBUS_reaction',usecols=(8,9,10,11,12))
#    outframe=pd.concat([df_vial, df_r, df_LID, df_Reagent], sort=False, axis=1)
#    df.to_excel('outtest.xls', sheet_name='NIMBUS_reaction', index=False)
#    print(df['Reagent2 (ul)'])
    print(rdf.to_string())


##Place holder function.  This can be fit to change the distribution of points at a later time. For now
## the method returns only the sobol value unmodified.  The sampling in each input x1, x2, x3 should be evenly distributed
## and unaltered.  (Blank function)
def f(x1, x2):
    return 0.0
#def f2(x1):
#    return 0.0

## Function SobolReagent generates the quasi-random distribution of points from the ranges indicated for each variable in the optunity.minimize function.
## The function returns a pandas array consisting of sobol distributed reagent concentrations as well as calculated columns for the other reagents
## The def f function above can be modified to bias the distribution.  See the optunity documentation for more help
def SobolReagent():
    _, info_random, _ = optunity.minimize(f, num_evals=96, x1=[50, 250], x2=[50,250], solver_name='sobol')
    _, info_FA, _ = optunity.minimize(f, num_evals=96, x1=[0, 60], x2=[0,60], solver_name='sobol')
    Reagent2=info_random.call_log['args']['x1'] #Create reagent amounts (uL), change x variable to change range, each generated from unique sobol index
    Reagent3=info_random.call_log['args']['x2']
#    Reagent4=info_random.call_log['args']['x1']
    Reagent5=info_FA.call_log['args']['x1']
    Reagent6=info_FA.call_log['args']['x2']
    rdf=pd.DataFrame()  #Construct primary data frames r2df=pd.DataFrame() 
    r2df=pd.DataFrame()
    r3df=pd.DataFrame()
    r4df=pd.DataFrame()
    r5df=pd.DataFrame()
    r6df=pd.DataFrame()
    r2df['Reagent2 (ul)'] = Reagent2  #insert data from the sobol construction into relevant data frame
    r3df['Reagent3 (ul)'] = Reagent3
    r4df['Reagent4 (ul)'] = 0.0
    r5df['Reagent5 (ul)'] = Reagent5 #Formic acid amounts are set to be non-equal 2 additions, 
    r6df['Reagent6 (ul)'] = Reagent6 # but this can be changed by setting r6df to equal Reagent6
    rdf_hold=pd.concat([r2df,r3df,r4df], sort=False, ignore_index=False, axis=1)  #Create reagent2-4 data frames
    print(rdf_hold)
    rdf=pd.concat([rdf_hold,r5df, r6df], sort=False, axis=1)
    print(rdf)
    rdf.fillna(value=0, inplace=True)
    r1df=(500-(rdf.iloc[:,0]+rdf.iloc[:,1]))
    rdf.insert(0,'Reagent1 (ul)', r1df)
    rdf_final=rdf.round(1)
    return(rdf_final)  ## Returns a pandas dataframe with all of the calculated reagent amounts.

    

#PrepareDirectory(RunID)
CreateRobotXLS()