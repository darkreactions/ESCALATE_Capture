from datetime import datetime, timezone
import json
import csv
from oauth2client.service_account import ServiceAccountCredentials
import Google_IO
import gspread
import os
import argparse as ap
import pandas as pd
import numpy as np
import optunity
import random
import matplotlib.pyplot as plt

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
lab = 'LBL'
readdate_gen=datetime.now(timezone.utc).isoformat()
readdate=readdate_gen.replace(':', '_') #Remove problematic characters
date=datetime.now(timezone.utc).strftime("%Y-%m-%d")
time=datetime.now(timezone.utc).strftime("%H_%M_%S")
RunID=readdate + "_" + lab #Agreed Upon format for final run information
#date='2017-10-20'
#time='22_59_29'
#readdate=date+"T"+time+".000000+00_00"
#RunID=readdate + "_" + lab #Agreed Upon format for final run information
print("Run Initiation (iso): ;;", readdate, file=log)  #Agreed Upon format for final run information
print("Run Initiation (iso):", readdate)  #Agreed Upon format for final run information

### Workflow 1 ###
### Simple Starting Points ### 
Debug = args.Debugging #Prevents editing the working directory and provides a dev mode as default
print("Debugging on (? - boolean) = ", Debug, end=' ;;\n', file=log)

# plot of chemical space??? ##
ploton=0
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print("Plotted (? -- boolean) = ", ploton, " ;;\n", end='\n', file=log)

Temp1 = 80
SRPM = 750
S1Dur = 900
S2Dur = 1200
Temp2 = 105
FinalHold = 12600

print("\n"
"Run Information -- ", " ;;\n" 
"Pre-reaction Temperature = ", "%s:celsius"%Temp1, " ;;\n" 
"Tray Shake Rate 1 (After First Addition) = ", "%s:RPM"%S1Dur, " ;;\n" 
"Tray Shake Rate 2 (After FAH addition) = ", "%s:RPM"%S2Dur, " ;;\n" 
"Reaction Temperature of Tray = ", "%s:celsius"%Temp2, " ;;\n"
"Duration held at final temperature = ", "%s:second"%FinalHold, " ;;\n" 
, end='\n', file=log)

### Link to amine list: https://goo.gl/UZSCBj ############
AMINE1 = "n-BuNH3I"
AMINE2 = "n-BuNH3I"

##Building Reagent List
reagentlist=[]
reagentlist.append(AMINE1)
reagentlist.append(AMINE2)
reagentlist.append('FAH')
reagentlist.append('PbI2')

##Key Variables throughout the code
ConcStock=1.5 #Maximum concentration of the stock solutions (A - PbI2 and amine, B - amine) in wkflow1
ConcStockAmine=6 #Maximum concentration of the stock solutions (A - PbI2 and amine, B - amine) in wkflow1
StockAAminePercent=2.00 #Percent concentration of amine in the first stock solution wkflow1
RTemp=45  # Reagent temperature prior to reaction start (sitting in block)
DeadVolume= 2.0 #Total dead volume in stock solutions
MaximumStockVolume=500.0 #Maximum volume of GBL, Stock A, and stockB
MaximumWellVolume=700.0

##Constraints
maxEquivAmine=4 #Maximum ratio of amine (value) to lead iodide
wellcount=96
molarmin1=0.40 #Lowest number of millimoles (mmol) added of amine or lead iodide to any well
molarminFA=2.0  #Lowest number of millimoles (mmol) added of formic acid (FAH) to any well
molarmaxFA=5.0 #Greatest number of millimoles (mmol) added of formic acid (FAH) to any well
molarmax1=(ConcStock*MaximumStockVolume/1000)  #Greatest number of millimoles (mmol) of lead iodidde added to any well
print("\n"
"Chemical Space Constraints -- ", " ;;\n" 
"Max Equiv Amine =", maxEquivAmine, ' ;;\n'
"Reaction Molar maximum =", molarmax1, ' ;;\n'
"Reaction Molar minimum =", molarmin1, ' ;;\n'
"Reaction Molar maximum FAH =", molarmaxFA, ' ;;\n'
"Reaction Molar minimum FAH =", molarminFA, ' ;;\n'
"Total Well Count = ", wellcount, " ;;\n" 
, end='\n', file=log)

##Reagent Preparation Settings
##Reagent 1
#R1PreTemp=
#R1StirRPM=
#R1Dur=

#Reagent 2
R2PreTemp=75
R2StirRPM=450
R2Dur=3600

#Reagent 3
R3PreTemp=75
R3StirRPM=450
R3Dur=3600

##Reagent 4
#R4PreTemp=
#R4StirRPM=
#R4Dur=
#
##Reagent 5
#R5PreTemp=
#R5StirRPM=
#R5Dur=
#
##Reagent 6
#R6PreTemp=
#R6StirRPM=
#R6Dur=

StockAAminePercent_Print = StockAAminePercent*100
print("\n"
"Stock Solution Variables -- ", " ;;\n" 
"Stock A Amine =", AMINE1, ' ;;\n'
"Stock A Info = ", "%s:celsius"%R2PreTemp , "%s:RPM"%R2StirRPM , "%s:second"%R2Dur, " ;;\n" 
"Stock B Amine =", AMINE2, ' ;;\n'
"Stock B Info = ", "%s:celsius"%R3PreTemp, "%s:RPM"%R3StirRPM, "%s:second"%R3Dur, " ;;\n" 
"Stock A Conc = ", "%s:Molar"%ConcStock, " ;;\n" 
"Stock A Amine Percent = ", "%s:Precent"%StockAAminePercent_Print, " ;;\n"
"Stock B Conc = ", "%s:Molar"%ConcStockAmine, " ;;\n" 
"Stock Temperature Prior to Addition = ", "%s:celsius"%RTemp, " ;;\n" 
"Dead Volume = ", "%s:milliliter"%DeadVolume, " ;;\n" 
"Maximum Combined Well Volume of Reagents 1-5 = ", "%s:microliter"%DeadVolume, " ;;\n" 
"Maximum Total Well Volume = ", "%s:microliter"%DeadVolume, " ;;\n" 
, end='\n', file=log)

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################


### General Setup Information ###
##GSpread Authorization information
scope= ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
gc =gspread.authorize(credentials)


### Directory and file collection handling###
##Generates new working directory with updated templates, return working folder ID
def NewWrkDir(RunID, Debug, robotfile, logfile): 
    NewDir=Google_IO.DriveCreateFolder(RunID, Debug)
    Google_IO.GupFile(NewDir, robotfile, logfile)
    file_dict=Google_IO.DriveAddTemplates(NewDir, RunID, Debug)
    return(file_dict) #returns the experimental data sheet google pointer url (GoogleID)

def ChemicalData():
    chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
    ChemicalBook = gc.open_by_key(chemsheetid)
    chemicalsheet = ChemicalBook.get_worksheet(0)
    with open('ChemicalIndex.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for line in chemicalsheet.get_all_values():
            writer.writerow(line)
    chemdf=pd.read_csv('ChemicalIndex.csv', index_col=1)
    return(chemdf)

### File preparation --- Main Code Body ###
##Updates all of the run data information and creates the empty template for amine information
def PrepareDirectory(RunID, robotfile, FinalAmountArray, logfile):
    new_dict=NewWrkDir(RunID, Debug, robotfile, logfile) #Calls NewWrkDir Function to get the list of files
    for key,val in new_dict.items(): 
        if "ExpDataEntry" in key: #Experimentalsheet = gc.open_bysearches for ExpDataEntry Form to get id
            sheetobject = gc.open_by_key(val).sheet1
            sheetobject.update_acell('B2', date) #row, column, replacement in experimental data entry form
            sheetobject.update_acell('B3', time)
            sheetobject.update_acell('B4', lab)
            sheetobject.update_acell('B6', RunID)
            sheetobject.update_acell('B17', AMINE1)
            sheetobject.update_acell('B20', AMINE2)
#            sheetobject.update_acell('C2', AMINE3)
            sheetobject.update_acell('D4', R2PreTemp)
            sheetobject.update_acell('E4', R2StirRPM)
            sheetobject.update_acell('F4', R2Dur)
            sheetobject.update_acell('D5', R3PreTemp)
            sheetobject.update_acell('E5', R3StirRPM)
            sheetobject.update_acell('F5', R3Dur)
            sheetobject.update_acell('C14', FinalAmountArray[0])
            sheetobject.update_acell('C16', FinalAmountArray[1])
            sheetobject.update_acell('C17', FinalAmountArray[2])
            sheetobject.update_acell('C18', FinalAmountArray[3])
            sheetobject.update_acell('C20', FinalAmountArray[4])
            sheetobject.update_acell('C21', FinalAmountArray[5])
            sheetobject.update_acell('C27', FinalAmountArray[6])
            sheetobject.update_acell('C28', FinalAmountArray[7])
            sheetobject.update_acell('B22', 'null')
            sheetobject.update_acell('E22', 'null')
            sheetobject.update_acell('B24', 'null')
            sheetobject.update_acell('B25', 'null')
            sheetobject.update_acell('B26', 'null')
            sheetobject.update_acell('C24', 'null')
            sheetobject.update_acell('C25', 'null')
            sheetobject.update_acell('C26', 'null')
            sheetobject.update_acell('E24', 'null')
            sheetobject.update_acell('E25', 'null')
            sheetobject.update_acell('E26', 'null')

##Place holder function.  This can be fit to change the distribution of points at a later time. For now
## the method returns only the sobol value unmodified.  The sampling in each input x1, x2, x3 should be evenly distributed
## and unaltered.  (Blank function)
def f(x1):
    return 0.0
def f2(x1, x2):
    return 0.0


##Function SobolReagent generates the quasi-random distribution of points from the ranges indicated for each variable in the optunity.minimize function.
## The function returns a pandas array consisting of sobol distributed reagent concentrations as well as calculated columns for the other reagents
## The def f function above can be modified to bias the distribution.  See the optunity documentation for more help
def SobolReagent(chemdf): 
    _, info_random, _ = optunity.minimize(f, num_evals=wellcount, x1=[molarmin1, molarmax1], solver_name='sobol')
    _, info_FA, _ = optunity.minimize(f2, num_evals=wellcount, x1=[molarminFA, (molarmaxFA/2)], x2=[molarminFA,(molarmaxFA/2)], solver_name='sobol')
    ##Create quasi-random data spread
    Reagentmm2=info_random.call_log['args']['x1'] #Create reagent amounts (mmol), change x variable to change range, each generated from unique sobol index
    Reagentmm3=[]
    #Generate a range of Amine concentrations dependent upon the range possible due to the presence of amine in Stock solution A \
    # The range is set to cover from the minimum physically possible through a X:1 ratio of Amine:PbI2.  Change the maxEquivAmine value to something to alter
    for mmolLeadI in Reagentmm2:
        molarminAmine=float(mmolLeadI)*StockAAminePercent #Set minimum to the physical limit (conc can't be lower than in the stock)
        ReagACheck=(mmolLeadI/ConcStock)
        if molarminAmine > molarmax1*StockAAminePercent: #If value of minimum is set too low, adjust the value to be reasonable
            molarminAmine=molarmax1*StockAAminePercent-molarmax1*.001*StockAAminePercent #Make sure that the minimum is always a little less (prevents breaking sobol)
            _, info_amine, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*maxEquivAmine], solver_name='sobol')
            newMolMinAmine=info_amine.call_log['args']['x1']
            newMolMinAmineUnpack=(newMolMinAmine[0])
            while (ReagACheck+((newMolMinAmineUnpack-mmolLeadI*StockAAminePercent)/ConcStockAmine)) > MaximumStockVolume/1000:  ## If the draw generates a maximum that would push the total well volume, redefine range and redraw
                _, info_amine2, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*maxEquivAmine], solver_name='sobol')
                newMolMinAmine=info_amine2.call_log['args']['x1']
                newMolMinAmineUnpack=(newMolMinAmine[0])
        else:  # if minimum is fine draw from full range
            _, info_amine, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*maxEquivAmine+mmolLeadI*maxEquivAmine*.001], solver_name='sobol')
            newMolMinAmine=info_amine.call_log['args']['x1']
            newMolMinAmineUnpack=(newMolMinAmine[0])
            count=0
            while (ReagACheck+((newMolMinAmineUnpack-mmolLeadI*StockAAminePercent)/ConcStockAmine)) > MaximumStockVolume/1000: ## If the draw generates a maximum that would push the total well volume, redefine range and redraw
                _, info_amine2, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*maxEquivAmine], solver_name='sobol')
                newMolMinAmine=info_amine2.call_log['args']['x1']
                newMolMinAmineUnpack=(newMolMinAmine[0])
                if count < 50:  # Sometimes the range between min and max is too tight and sobol doesn't behave well.  This sets the value of the amine stock to the remainder of the well volume
                    if ReagACheck > 0.48:
                        newMolMinAmineUnpack=(.500-ReagACheck)*ConcStockAmine+mmolLeadI*StockAAminePercent
                if count > 50: # Should prevent death loop.... but the code hasn't been finished.  For the most part this code shouldn't be needed until UI on DRP is finished
                    print("Amine Ratio Maximum Very High. Strongly Recommend Adjusting")
                    newMolMinAmineUnpack=0
                    print(ReagACheck, newMolMinAmineUnpack)
                    break 
        Reagentmm3.append(newMolMinAmineUnpack) # Append the value for the calculated mmol of amine to the list

    # Create Formic Acid data frames
    Reagentmm5=info_FA.call_log['args']['x1']
    Reagentmm6=info_FA.call_log['args']['x2']
    # create data frames of target mmol of material
    rmmdf=pd.DataFrame()  #Construct primary data frames r2df=pd.DataFrame()  r2df means reagent 2 dataframe
    rmmdf2=pd.DataFrame()  #Construct primary data frames r2df=pd.DataFrame()  r2df means reagent 2 dataframe
    rmmdf.insert(0, "PbI2 mmol", Reagentmm2)
    rmmdf.insert(1, "Amine mmol 2", Reagentmm3)
    rmmdf2.insert(0, "FA mmol", Reagentmm5)
    rmmdf2.insert(1, "FA2 mmol", Reagentmm6)
    # Debugging - Show concentration graph of pbI2 and amine
    if ploton == 1:
        fig, ax=plt.subplots()
        ax.scatter(rmmdf.iloc[:,0],rmmdf.iloc[:,1])
        ax.set_xlabel('mmol PbI2')
        ax.set_ylabel('mmol %s'% AMINE1)
        plt.show()
    else: pass
    # Convert mmol into the actual amounts of stock solution
    Stock={'Stock A':[ConcStock,StockAAminePercent*ConcStock],'Stock B':[0,ConcStockAmine]} #Stock A is the mixture, B is all amine
    Stockdf=pd.DataFrame(data=Stock)
    rmmdf_trans=rmmdf.transpose()
    rmmdf.insert(2, "FA mmol", Reagentmm5)
    rmmdf.insert(3, "FA2 mmol", Reagentmm6)
    print("moles Array :{ \n", rmmdf, "\n}", file=log)
    # Converting the mmol of the reagents to volumes of the stock solutions in each well
    Stockdf_inverse= pd.DataFrame(np.linalg.pinv(Stockdf.values))
    npVols=np.transpose(np.dot(Stockdf_inverse, rmmdf_trans))  #Unrefined matrix of Volumes of the stock solutions needed for each well in the robotics run
    # Calculating the total volume of formic acid needed for each run 
    rmmdf3=rmmdf2*chemdf.loc["FAH","Molecular Weight (g/mol)"] / chemdf.loc["FAH","Density            (g/mL)"]
    rmmdf4=rmmdf3.rename(columns={"FA mmol":"Reagent5 (ul)", "FA2 mmol": "Reagent6 (ul)" })
    npVolsdf=pd.DataFrame({"Reagent2 (ul)": npVols[:,0], "Reagent3 (ul)": npVols[:,1]})*1000
    # Setting up the remaining data frames
    rdf=(pd.concat([npVolsdf,rmmdf4], axis=1)) #Main dataframe containing the total volumes of the reagents for the robot
    r1df=(MaximumStockVolume-(rdf.iloc[:,0]+rdf.iloc[:,1])) #Calculates the remaining volume of GBL needed for the reaction r4df=(rdf.iloc[:,0]*0)  #Creates a correctly sized column of zeros
    r4df=(r1df*0)
    rdf.insert(0,'Reagent1 (ul)', r1df)
    rdf.insert(3,'Reagent4 (ul)', r4df)
    return(rdf.round())  ##Returns a pandas dataframe with all of the calculated reagent amounts.


## Prepares directory and relevant files, calls upon code to operate on those files to generate a new experimental run (workflow 1)
def CreateRobotXLS():
#    chemdf=pd.read_csv('ChemicalIndex.csv', index_col=1)
    chemdf=ChemicalData() #Retrieves information regarding chemicals and performs a vlookup on the generated dataframe
    rdf=SobolReagent(chemdf) #Brings in the datafram containing all of the volumes of solutions
    #Failsafe check for total volumes
    maxVolR1R2=(rdf.loc[:,"Reagent2 (ul)"]+rdf.loc[:, "Reagent3 (ul)"]).max()
#    print(maxVolR1R2)
    maxVol=(rdf.loc[:,"Reagent1 (ul)"]+rdf.loc[:,"Reagent2 (ul)"]+rdf.loc[:, "Reagent3 (ul)"]+rdf.loc[:, "Reagent4 (ul)"]+rdf.loc[:, "Reagent5 (ul)"]+rdf.loc[:, "Reagent6 (ul)"]).max()
    while maxVol > MaximumWellVolume:
        rdf=[]
        print(maxVol, 'Volume Error')
        rdf=SobolReagent(chemdf)
        maxVol=(rdf.loc[:,"Reagent1 (ul)"]+rdf.loc[:,"Reagent2 (ul)"]+rdf.loc[:, "Reagent3 (ul)"]+rdf.loc[:, "Reagent4 (ul)"]+rdf.loc[:, "Reagent5 (ul)"]+rdf.loc[:, "Reagent6 (ul)"]).max()
    print("\nStock Solution Final Amounts -- ;;", file=log)
    print(int(maxVol),'(ul) Max Calculated < %i (ul) Max Allowed Well Volume ;;'%MaximumWellVolume, file=log)
    #Constructing output information for creating the experimental excel input sheet
    solventvolume=rdf['Reagent1 (ul)'].sum()+DeadVolume*1000 #Total volume of the stock solution needed for the robot run
    print('Solvent: ', (solventvolume/1000).round(2), " mL solvent ;;", sep='', file=log)
    stockAvolume=rdf['Reagent2 (ul)'].sum()+DeadVolume*1000 #Total volume of the stock solution needed for the robot run
    PbI2mol=(stockAvolume/1000/1000*ConcStock)
    PbI2mass=(PbI2mol*chemdf.loc["PbI2", "Molecular Weight (g/mol)"])
    aminemassA=(stockAvolume/1000/1000*ConcStock*StockAAminePercent*chemdf.loc[AMINE1, "Molecular Weight (g/mol)"])
    print('Stock Solution A: ', (stockAvolume/1000).round(2), " mL solvent, ", PbI2mass.round(2), " g PbI2, ", aminemassA.round(2), " g ", AMINE1, " ;;", sep='',file=log)
    stockBvolume=rdf['Reagent3 (ul)'].sum()+DeadVolume*1000 #Total volume of the stock solution needed for the robot run
    Aminemol=(stockBvolume/1000/1000*ConcStockAmine)
    aminemassB=(Aminemol*chemdf.loc[AMINE1, "Molecular Weight (g/mol)"])
    print('Stock Solution B: ', (stockBvolume/1000).round(2), " mL solvent, ", aminemassB.round(2), " g ", AMINE1, " ;;", sep='', file=log)
    stockFormicAcid5=rdf['Reagent5 (ul)'].sum()+DeadVolume*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid6=rdf['Reagent6 (ul)'].sum()+DeadVolume*1000 #Total volume of the stock solution needed for the robot run
    #assign correct liquid class to the sample handler
    hv='HighVolume_Water_DispenseJet_Empty'
    sv='StandardVolume_Water_DispenseJet_Empty'
    lv='LowVolume_Water_DispenseJet_Empty'
    x=1
    vol_ar=[]
    while x <=6:
        name=('maxVolreag%i' %x)
        name_maxvol=(rdf.loc[:,"Reagent%i (ul)" %(x)]).max()
        x+=1
        if name_maxvol >= 300:
            vol_ar.append(hv)
        if name_maxvol >= 50 and name_maxvol <300:
            vol_ar.append(sv)
        if name_maxvol < 50:
            vol_ar.append(lv)
    #Handle and output dataframes
    df_Tray=pd.read_excel('Template.xls', sheet_name='NIMBUS_reaction',usecols=(0,1))
    df_Tray=pd.read_excel('Template.xls', sheet_name='NIMBUS_reaction',usecols=(0,1))
    Parameters={
    'Reaction Parameters':['Temperature (C):','Stir Rate (rpm):','Mixing time1 (s):','Mixing time2 (s):', 'Reaction time (s):',""], 
    'Parameter Values':[Temp2, SRPM, S1Dur, S2Dur, FinalHold,''],
    }
    Conditions={
    'Reagents':['Reagent1', "Reagent2", "Reagent3", "Reagent4",'Reagent5','Reagent6'],
    'Reagent identity':['Reagent1', "Reagent2", "Reagent3", "Reagent4",'Reagent5','Reagent6'],
    'Liquid Class':vol_ar,
    'Reagent Temperature':[RTemp,RTemp,RTemp,RTemp,RTemp,RTemp]
    }
    df_parameters=pd.DataFrame(data=Parameters)
    df_conditions=pd.DataFrame(data=Conditions)
    outframe=pd.concat([df_Tray.iloc[:,0],rdf,df_Tray.iloc[:,1],df_parameters, df_conditions], sort=False, axis=1)
    FinalAmountArray_hold=[]
    FinalAmountArray_hold.append((solventvolume/1000).round(2))
    FinalAmountArray_hold.append(PbI2mass.round(2))
    FinalAmountArray_hold.append((aminemassA.round(2)))
    FinalAmountArray_hold.append((stockAvolume/1000).round(2))
    FinalAmountArray_hold.append(aminemassB.round(2))
    FinalAmountArray_hold.append((stockBvolume/1000).round(2))
    FinalAmountArray_hold.append((stockFormicAcid5/1000).round(2))
    FinalAmountArray_hold.append((stockFormicAcid6/1000).round(2))
    log.close()
    os.rename('LogFile.txt', "%s_LogFile.txt"%RunID)
    outframe.to_excel("%s_RobotInput.xls" %RunID, sheet_name='NIMBUS_reaction', index=False)
    robotfile=("%s_RobotInput.xls" %RunID)
    logfile=("%s_LogFile.txt"%RunID)

    PrepareDirectory(RunID, robotfile, FinalAmountArray_hold, logfile) #Significant online operation, slow.  Comment out to test .xls generation (robot file) portions of the code more quickly
#    return(rdf)

CreateRobotXLS()
