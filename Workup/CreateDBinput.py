import json
from pathlib import Path
import csv
from oauth2client.service_account import ServiceAccountCredentials
import Google_IO_DBsetup
import gspread
import os
import argparse as ap
import pandas as pd
import numpy as np
import pprint

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

## Set the workflow of the code used to generate the experimental data and to process the data
WFSet=1.0

### Simple Starting Points ### 
Debug = args.Debugging #Prevents editing the working directory and provides a dev mode as default
#print("Debugging on (? - boolean) = ", Debug, end=' ;;\n', file=log)

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

def Expdata(DatFile):
    ExpEntry=DatFile
    with open(ExpEntry, "r") as file1:
        file1out=json.load(file1)
        lines=(json.dumps(file1out, indent=4, sort_keys=True))
    lines=lines[:-4]
    return(lines)
    ## File processing for the experimental JSON to convert to the final form (header of the script)

def Robo(robotfile):
    #o the file handling for the robot.xls file and return a JSON object
    robo_df = pd.read_excel(open(robotfile,'rb'), sheet_name=0,usecols=7)
    robo_df_2 = pd.read_excel(open(robotfile,'rb'), sheet_name=0,usecols=(8,9)).dropna()
    robo_df_3 = pd.read_excel(open(robotfile,'rb'), sheet_name=0,usecols=(10,11,12,13)).dropna()
    robo_dump=json.dumps(robo_df.values.tolist())
    robo_dump2=json.dumps(robo_df_2.values.tolist())
    robo_dump3=json.dumps(robo_df_3.values.tolist())
    return(robo_dump, robo_dump2, robo_dump3)

def Crys(crysfile):
    ##Gather the crystal datafile information and return JSON object
    crys_df=pd.read_csv(open(crysfile, 'r'), usecols=(3,4))
    crys_list=crys_df.values.tolist()
    crys_dump=json.dumps(crys_list)
    return(crys_dump)

def genthejson(Outfile, workdir, opfolder):
    ## Do all of the file handling for a particular run and assemble the JSON, return the completed JSON file object
    ## and location for sorting and final comparison

    Crysfile=workdir+opfolder+'_CrystalScoring.csv'
    Expdatafile=workdir+opfolder+'_ExpDataEntry.json'
    Robofile=workdir+opfolder+'_RobotInput.xls'
    exp_return=Expdata(Expdatafile)
    robo_return=Robo(Robofile)
    crys_return=Crys(Crysfile)
    print(exp_return, file=Outfile)
    print('\t},', file=Outfile)
    print('\t', '"well_volumes":', file=Outfile)
    print('\t', robo_return[0], ',', file=Outfile)
    print('\t', '"tray_environment":', file=Outfile)
    print('\t', robo_return[1], ',', file=Outfile)
    print('\t', '"robot_reagent_handling":', file=Outfile)
    print('\t', robo_return[2], ',', file=Outfile)
    print('\t', '"crys_file_data":', file=Outfile)
    print('\t', crys_return, file=Outfile)
    print('}', file=Outfile)

def ExpDirOps():
    ##Call code to get all of the relevant folder titles from the experimental directory and
#    Google_IO_DBsetup.drivedatfold()
    ##Cross reference with the working directory of the final Json files send the list of jobs needing processing
    ## loops of IFs for file checking
    opdir='13xmOpwh-uCiSeJn8pSktzMlr7BaPDo7B'
    ExpList=Google_IO_DBsetup.drivedatfold(opdir)
    crys_dict=(ExpList[0])
    robo_dict=(ExpList[1])
    Expdata=(ExpList[2])
    dir_dict=(ExpList[3])
    for folder in dir_dict:
        exp_json=Path("FinalizedJSON/%s.json" %folder)
        if exp_json.is_file():
            print(folder)
            print('exists')
        else:
            Outfile=open(exp_json, 'w')
            workdir='datafiles/'
            rxnfileUIDs=Google_IO_DBsetup.getalldata(crys_dict[folder],robo_dict[folder],Expdata[folder], workdir, folder)
            print(folder)
            genthejson(Outfile, workdir, folder)
            Outfile.close()
#            with open(exp_json, 'r') as the_json:
#                theOut=json.load(the_json)
#                print(exp_json, "Successfully Generated")
ExpDirOps()

