import json
import csv
from oauth2client.service_account import ServiceAccountCredentials
import Google_IO
import gspread
import os
import argparse as ap
import pandas as pd
import numpy as np

##########################################################
#  _        ___           _                              #
# |_)    o   |   _. ._   |_) _  ._   _| |  _ _|_  _  ._  #
# |_) \/ o  _|_ (_| | |  |  (/_ | | (_| | (/_ |_ (_) | | #
#     /                                                  #
##########################################################

### Command line parsing for taking data from shell script
parser = ap.ArgumentParser(description='Requires Debug to be manually toggled on')
parser.add_argument('Debugging', default=1, type=int, help='') #Default, debugging on and real code off == "1"
args = parser.parse_args()
log=open("LogFile.txt", "w")


##Setup Run ID Information

### Workflow 1 ###
### Simple Starting Points ### 
Debug = args.Debugging #Prevents editing the working directory and provides a dev mode as default
print("Debugging on (? - boolean) = ", Debug, end=' ;;\n', file=log)

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

### General Setup Information ###
##GSpread Authorization information
#scope= ['https://spreadsheets.google.com/feeds']
#credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
#gc =gspread.authorize(credentials)




### Directory and file collection handling###
##Generates new working directory with updated templates, return working folder ID
#def NewWrkDir(RunID, Debug, robotfile, logfile): 
#    NewDir=Google_IO.DriveCreateFolder(RunID, Debug)
#    Google_IO.GupFile(NewDir, robotfile, logfile)
#    file_dict=Google_IO.DriveAddTemplates(NewDir, RunID, Debug)
#    return(file_dict) #returns the experimental data sheet google pointer url (GoogleID)
#
#def ChemicalData():
#    chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
#    ChemicalBook = gc.open_by_key(chemsheetid)
#    chemicalsheet = ChemicalBook.get_worksheet(0)
#    with open('ChemicalIndex.csv', 'w') as f:
#        writer = csv.writer(f, delimiter=',')
#        for line in chemicalsheet.get_all_values():
#            writer.writerow(line)
#    chemdf=pd.read_csv('ChemicalIndex.csv', index_col=1)
#    return(chemdf)

### File preparation --- Main Code Body ###
##Updates all of the run data information and creates the empty template for amine information
#def PrepareDirectory(RunID, robotfile, FinalAmountArray, logfile):
#    new_dict=NewWrkDir(RunID, Debug, robotfile, logfile) #Calls NewWrkDir Function to get the list of files
#    for key,val in new_dict.items(): 
#        if "ExpDataEntry" in key: #Experimentalsheet = gc.open_bysearches for ExpDataEntry Form to get id
#            sheetobject = gc.open_by_key(val).sheet1
#            sheetobject.update_acell('B2', date) #row, column, replacement in experimental data entry form
#            sheetobject.update_acell('B3', time)
#            sheetobject.update_acell('B4', lab)
#            sheetobject.update_acell('B6', RunID)
#
#
#    Stock={'Stock A':[ConcStock,StockAAminePercent*ConcStock],'Stock B':[0,ConcStockAmine]} #Stock A is the mixture, B is all amine
#    Stockdf=pd.DataFrame(data=Stock)
#    rmmdf_trans=rmmdf.transpose()
#    rmmdf.insert(2, "FA mmol", Reagentmm5)
#    rmmdf.insert(3, "FA2 mmol", Reagentmm6)
#    Stockdf_inverse= pd.DataFrame(np.linalg.pinv(Stockdf.values))