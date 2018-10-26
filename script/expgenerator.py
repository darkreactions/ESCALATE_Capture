#Copyright (c) 2018 Ian Pendleton - MIT License
import os
import logging
from script import rxnprng
from script import reactantclasses
import json
import csv
#from script import googleio
#from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
import numpy as np
import sys
import logging
from script import testing


# create logger
modlog = logging.getLogger('initialize.expgenerator')


### Directory and file collection handling###
##Generates new working directory with updated templates, return working folder ID
def NewWrkDir(robotfile, rxndict): 
    print(rxndict['RunID'])
    scope= ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc =gspread.authorize(credentials)
    NewDir=googleio.DriveCreateFolder(rxndict['RunID'])
    googleio.GupFile(NewDir, robotfile, rxndict)
    file_dict=googleio.DriveAddTemplates(NewDir, rxndict['RunID'])
    return(file_dict) #returns the experimental data sheet google pointer url (GoogleID)

def ChemicalData():
    print('Obtaining chemical information from Google Drive.. \n', end='')
    chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
    ChemicalBook = gc.open_by_key(chemsheetid)
    chemicalsheet = ChemicalBook.get_worksheet(0)
    chemical_list = chemicalsheet.get_all_values()
    chemdf=pd.DataFrame(chemical_list, columns=chemical_list[0])
    chemdf=chemdf.iloc[1:]
    chemdf=chemdf.reset_index(drop=True)
    chemdf=chemdf.set_index(['Chemical Abbreviation'])
    return(chemdf)

### File preparation --- Main Code Body ###
##Updates all of the run data information and creates the empty template for amine information
def PrepareDirectory(robotfile, FinalAmountArray, rxndict):
    new_dict=NewWrkDir(robotfile, rxndict) #Calls NewWrkDir Function to get the list of files
    print('Writing final values to experimental data entry form.....')
    for key,val in new_dict.items(): 
        if "ExpDataEntry" in key: #Experimentalsheet = gc.open_bysearches for ExpDataEntry Form to get id
            sheetobject = gc.open_by_key(val).sheet1
            sheetobject.update_acell('B2', rxndict['date']) #row, column, replacement in experimental data entry form
            sheetobject.update_acell('B3', rxndict['time'])
            sheetobject.update_acell('B4', rxndict['lab'])
            sheetobject.update_acell('B6', rxndict['RunID'])
            sheetobject.update_acell('B7', rxndict['ExpWorkflowVer'])
            sheetobject.update_acell('B8', rxndict['RoboVersion'])
            sheetobject.update_acell('B9', 'null')
            sheetobject.update_acell('B10', 'null')
            sheetobject.update_acell('B11', 'null')
            sheetobject.update_acell('B16', rxndict['chem2_abbreviation'])
            sheetobject.update_acell('B17', rxndict['chem3_abbreviation'])
            sheetobject.update_acell('B20', rxndict['chem3_abbreviation'])
#            sheetobject.update_acell('C2', AMINE3)
            sheetobject.update_acell('D4', rxndict['reagents_prep_temperature'])
            sheetobject.update_acell('E4', rxndict['reagents_prep_stirrate'])
            sheetobject.update_acell('F4', rxndict['reagents_prep_duration'])
            sheetobject.update_acell('D5', rxndict['reagents_prep_temperature'])
            sheetobject.update_acell('E5', rxndict['reagents_prep_stirrate'])
            sheetobject.update_acell('F5', rxndict['reagents_prep_duration'])
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

#Constructs well array information based on the total number of wells for the run
#Future versions could do better at controlling the specific location on the tray that reagents are dispensed.  This would be place to start
# that code overhaul
# will not work for workflow 3
def MakeWellList(rxndict):
    wellorder=['A', 'C', 'E', 'G', 'B', 'D', 'F', 'H'] #order is set by how the robot draws from the solvent wells
    VialList=[]
    welllimit=rxndict['wellcount']/8+1
    count=1
    while count<welllimit:
        for item in wellorder:
            countstr=str(count)
            Viallabel=item+countstr
            VialList.append(Viallabel)
        count+=1
    df_VialInfo=pd.DataFrame(VialList)
    df_VialInfo.columns=['Vial Site']
    df_VialInfo['Labware ID:']=rxndict['plate_container'] 
    return(df_VialInfo)

#Defines what type of liquid class sample handler (pipette) will be needed for the run
def volarray(rdf):
    hv='HighVolume_Water_DispenseJet_Empty'
    sv='StandardVolume_Water_DispenseJet_Empty'
    lv='LowVolume_Water_DispenseJet_Empty'
    x=1
    vol_ar=[]
    while x <=6:
        name_maxvol=(rdf.loc[:,"Reagent%i (ul)" %(x)]).max()
        x+=1
        if name_maxvol >= 300:
            vol_ar.append(hv)
        if name_maxvol >= 50 and name_maxvol <300:
            vol_ar.append(sv)
        if name_maxvol < 50:
            vol_ar.append(lv)
    return(vol_ar)

def conreag(rxndict, rdf, chemdf):
    #Constructing output information for creating the experimental excel input sheet
    solventvolume=rdf['Reagent1 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockAvolume=rdf['Reagent2 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid5=rdf['Reagent5 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid6=rdf['Reagent6 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run

    PbI2mol=(stockAvolume/1000/1000*rxndict['reag2_target_conc_chemical2'])
    PbI2mass=(PbI2mol*float(chemdf.loc["PbI2", "Molecular Weight (g/mol)"]))
    StockAAminePercent=(rxndict['reag2_target_conc_chemical3']/rxndict['reag2_target_conc_chemical2'])
  #  aminemassA=(stockAvolume/1000/1000*rxndict['reag2_target_conc_chemical2']*StockAAminePercent*float(chemdf.loc[rxndict['chem3_abbreviation'], "Molecular Weight (g/mol)"]))
    stockBvolume=rdf['Reagent3 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
  #  Aminemol=(stockBvolume/1000/1000*rxndict['reag3_target_conc_chemical2'])
    aminemassB=(Aminemol*float(chemdf.loc[rxndict['chem2_abbreviation'], "Molecular Weight (g/mol)"]))

    #The following section handles and output dataframes to the format required by the robot.xls file.  File type is very picky about white space and formatting.  
    df_Tray=MakeWellList(rxndict)
    vol_ar=volarray(rdf)
    Parameters={
    'Reaction Parameters':['Temperature (C):','Stir Rate (rpm):','Mixing time1 (s):','Mixing time2 (s):', 'Reaction time (s):',""], 
    'Parameter Values':[rxndict['temperature2_nominal'], rxndict['stirrate'], rxndict['duratation_stir1'], rxndict['duratation_stir2'], rxndict['duration_reaction'] ,''],
    }
    Conditions={
    'Reagents':['Reagent1', "Reagent2", "Reagent3", "Reagent4",'Reagent5','Reagent6'],
    'Reagent identity':['1', "2", "3", "4",'5','6'],
    'Liquid Class':vol_ar,
    'Reagent Temperature':[rxndict['reagents_prerxn_temperature'],rxndict['reagents_prerxn_temperature'],rxndict['reagents_prerxn_temperature'],rxndict['reagents_prerxn_temperature'],rxndict['reagents_prerxn_temperature'],rxndict['reagents_prerxn_temperature']]
    }
    df_parameters=pd.DataFrame(data=Parameters)
    df_conditions=pd.DataFrame(data=Conditions)
    outframe=pd.concat([df_Tray.iloc[:,0],rdf,df_Tray.iloc[:,1],df_parameters, df_conditions], sort=False, axis=1)
    outframe.to_excel("localfiles/%s_RobotInput.xls" %rxndict['RunID'], sheet_name='NIMBUS_reaction', index=False)
    FinalAmountArray_hold=[]
    FinalAmountArray_hold.append((solventvolume/1000).round(2))
    FinalAmountArray_hold.append(PbI2mass.round(2))
    FinalAmountArray_hold.append((aminemassA.round(2)))
    FinalAmountArray_hold.append((stockAvolume/1000).round(2))
    FinalAmountArray_hold.append(aminemassB.round(2))
    FinalAmountArray_hold.append((stockBvolume/1000).round(2))
    FinalAmountArray_hold.append((stockFormicAcid5/1000).round(2))
    FinalAmountArray_hold.append((stockFormicAcid6/1000).round(2))
    return(FinalAmountArray_hold)


def expwellcount(rxndict, exp, exp_wells,edict):
    # if already configured with all well counts explicityly defined, return an unaltered well count dict
    # else do some checks on the manual entry and add specific well count values where appropriate
    # assumes that any well count values not explicitly defined will be divided amongst the non-defined experiments
    basewellcount = []
    expwithwells = []
    # Calculates how many experimental wells have been manually assigned
    for k,v in exp_wells.items():
        basewellcount.append(v)
        expwithwells.append(k.split('_')[0])
    forremaining = (rxndict['wellcount'] - sum(basewellcount))
    # If the number of wells being manually specified exceeds the tray limit (user defined), exit.
    if (sum(basewellcount)) > rxndict['wellcount']:
        modlog.error("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
        print("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
        sys.exit()
    # ensures that the total number of wells targeted for the tray is correctly specified. Too few wells specified means the user isn't paying attention!
    elif len(exp) == len(exp_wells):
        if (sum(basewellcount)) < rxndict['wellcount']:
            print(forremaining, 'wells remain unallocated. Please check settings')
        else:
            pass
    # Divide up remaining wells and assign appropriately
    else:
        if (sum(basewellcount)) > rxndict['wellcount']:
            modlog.error("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
            print("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
            sys.exit()
        else: 
            addwellexplist = []
            for experiment,reagents in exp.items():
                if experiment in expwithwells:
                    pass
                else:
                    addwellexplist.append(experiment+'_wells')
            wellsdivided = (forremaining / len(addwellexplist))
            for entry in addwellexplist:
                rxndict[entry] = wellsdivided
                edict[entry] = wellsdivided
    print("Wells for experiments successfully implemented")
    return(rxndict, edict)


# This sort of parsing is needed to ensure that the diversity of experiments that we geenrate throughout this process is scalable
# We don't want to be limited on the nubmer of reactions that can be considered for a single plate.  
# Lots of things need to be organized sequentially.  This code is written out long form to make the manipulations more interpretable
def expbuild(rxndict, rdict): # parse the reaction dictionary and reagent diction for relevant information
    # pull out only the terms with exp in the name (just consider and manipulate user defined variables) this will break if user adds variables with no default processing, that breaking is intentional
    edict = {}
    for k,v in rxndict.items(): #get out all of the information about experiments (the chemicals and the associated volumes and well counts)
        if 'exp' in k:
            edict[k] = v
    exp = {}
    exp_vols = {}
    exp_wells = {}
    #separate out the experimetnatl informatio nadn the volume information
    for entry,value in edict.items(): #isolate the information about experiments and the volumes, but keep them linked
        if 'vol' in entry:
            updatedname = entry.split("_")
            exp_vols[updatedname[0]] = value
        # some code to make sure that manually selected numbers of wells can be parsed and the remaining automatatically divided
        elif 'wells' in entry:
            exp_wells[entry] = value
        else:
            exp[entry] = value
    # Determine how many different xperiments are running on this tray
    expeval = 1
    edict_coded = {}
    totalexperiments = (len(exp))
    # divide remaining wells not manually assigned for the other experiments, add the well count to exp_wells dict and rxndict for later use.
    rxndict['totalexperiments'] = totalexperiments
    (rxndict, edict) = expwellcount(rxndict, exp, exp_wells, edict)
    # Use the experimental information to create a unique experiemnt for each well based on the general experimental constraints (use class object ot keep track of volumes)
    # Each particular subdivision of wells (each exp grouping) is added to the dictionary of overall experiments and returned
    return(rxndict, edict)

#custom function built to parse the current version of the runme.py script.
#This function operates specifcially to move the information from the initial user input into the reagent class for later use
def buildreagents(rxndict, chemdf):
    reagentlist=[]
    reagentdict={}
    #find all of the reagents constructured in the run
    for item in rxndict:
        if 'reag' in item and "chemicals" in item:
            reagentname=(item.split('_'))
            reagentlist.append(reagentname[0])
    #Turn all of those reagents into class objects
    for entry in reagentlist:
        reagentvariables={}
        reagentvariables['reagent']=entry
        entry_num = entry.split('g')
        for variable,value in rxndict.items(): 
            if entry in variable:
                variable=(variable.split('_',1))
                reagentvariables[variable[1]]=value
        reagent=reactantclasses.perovskitereagent(reagentvariables, rxndict, entry_num[1])  # should scale nicely, class can be augmented without breaking the code
        #return the class objects in a new dictionary for later use!
        reagentdict[entry_num[1]]=reagent
    return(reagentdict)

def chemicallimits(rxndict):
    climits = {}
    for k,v in rxndict.items():
        if "chem" in k and "molarmin" in k:
            climits[k] = v
        if "chem" in k and "molarmax" in k:
            climits[k] = v
    return(climits)
        


## Prepares directory and relevant files, calls upon code to operate on those files to generate a new experimental run (workflow 1)
def datapipeline(rxndict):
    testing.prebuildvalidation(rxndict) # testing to ensure that the user defined parameters match code specs.  
    #Dataframe containing all of the chemical information
    chemdf=pd.read_csv('ChemicalIndex.csv', index_col=1)
    #Dictionary with the user defined chemical limits for later use
    climits = chemicallimits(rxndict)
#    chemdf=ChemicalData() #Retrieves information regarding chemicals and performs a vlookup on the generated dataframe
    # Build a dictionary of the information on each reagent.  Can be inspected in the log file if needed
    rdict=buildreagents(rxndict, chemdf)
    for k,v in rdict.items():
        modlog.info("%s : %s" %(k,vars(v)))
    # Build a dictionary for experimental construction and constraints
    # Send off the experiments to be built using the reagents and the experimental constraints from the rxndict chemicals (soon to be synbiohub and user settings)
    (rxndict, edict)=expbuild(rxndict, rdict)
    # Some basic experiment validation and error reporting.  Checks the user constraints prior to executing the sampling method
    testing.postbuildvalidation(rxndict,rdict,edict) # some basic in line code to make sure that the experiment and reagents have been correctly constructed by the user
    #Send out all of the constraints and chemical information for run assembly
    rdf1=rxnprng.preprocess(chemdf, rxndict, edict, rdict, climits) 


#    FinalAmountArray_hold =  conreag(rxndict,rdf1, chemdf)
    robotfile=("localfiles/%s_RobotInput.xls" %rxndict['RunID'])
#    PrepareDirectory(robotfile, FinalAmountArray_hold, rxndict) #Significant online operation, slow.  Comment out to test .xls generation (robot file) portions of the code more quickly
    print("Job Creation Complete")
