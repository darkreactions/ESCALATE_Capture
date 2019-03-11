#Copyright (c) 2018 Ian Pendleton - MIT License
import os
import sys
import logging
import json
import csv
import logging
import numpy as np
import pandas as pd
from pandas import ExcelWriter

from capture import testing
from capture import rxnprng
from capture.models import reagent
from capture.models import chemical

# create logger
modlog = logging.getLogger('capture.expgenerator')

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

#Defines what type of liquid class sample handler (pipette) will be needed for the run, these are hardcoded to the robot
def volarray(rdf, maxr):
    hv='HighVolume_Water_DispenseJet_Empty'
    sv='StandardVolume_Water_DispenseJet_Empty'
    lv='Tip_50ul_Water_DispenseJet_Empty'
    x=1
    vol_ar=[]
    while x <= maxr:
        name_maxvol=(rdf.loc[:,"Reagent%i (ul)" %(x)]).max()
        if name_maxvol >= 300:
            vol_ar.append(hv)
        elif name_maxvol >= 50 and name_maxvol <300:
            vol_ar.append(sv)
        elif name_maxvol < 50:
            vol_ar.append(lv)
        x+=1
    return(vol_ar)


def preprobotfile(rxndict, vardict, erdf):
    df_Tray=MakeWellList(rxndict)
    vol_ar=volarray(erdf, vardict['max_robot_reagents'])
    Parameters={
    'Reaction Parameters':['Temperature (C):','Stir Rate (rpm):','Mixing time1 (s):','Mixing time2 (s):', 'Reaction time (s):',""], 
    'Parameter Values':[rxndict['temperature2_nominal'], rxndict['stirrate'], rxndict['duratation_stir1'], rxndict['duratation_stir2'], rxndict['duration_reaction'] ,''],
    }
    Conditions={
    'Reagents':['Reagent1', "Reagent2", "Reagent3", "Reagent4",'Reagent5','Reagent6','Reagent7'],
    'Reagent identity':['1', "2", "3", "4",'5','6','7'],
    'Liquid Class':vol_ar,
    'Reagent Temperature':[rxndict['reagents_prerxn_temperature']]*len(vol_ar)}
    df_parameters=pd.DataFrame(data=Parameters)
    df_conditions=pd.DataFrame(data=Conditions)
    outframe=pd.concat([df_Tray.iloc[:,0],erdf,df_Tray.iloc[:,1],df_parameters, df_conditions], sort=False, axis=1)
    robotfile = ("localfiles/%s_RobotInput.xls" %rxndict['RunID'])
    outframe.to_excel(robotfile, sheet_name='NIMBUS_reaction', index=False)
    return(robotfile)


def conreag(rxndict, rdf, chemdf, rdict, robotfile):
    #Constructing output information for creating the experimental excel input sheet
    solventvolume=rdf['Reagent1 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockAvolume=rdf['Reagent2 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid6=rdf['Reagent6 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid7=rdf['Reagent7 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run

    PbI2mol=(stockAvolume/1000/1000*rxndict['reag2_target_conc_chemical2'])
    PbI2mass=(PbI2mol*float(chemdf.loc["PbI2", "Molecular Weight (g/mol)"]))
    StockAAminePercent=(rxndict['reag2_target_conc_chemical3']/rxndict['reag2_target_conc_chemical2'])
    aminemassA=(stockAvolume/1000/1000*rxndict['reag2_target_conc_chemical2']*StockAAminePercent*float(chemdf.loc[rxndict['chem3_abbreviation'], "Molecular Weight (g/mol)"]))
    stockBvolume=rdf['Reagent3 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    Aminemol=(stockBvolume/1000/1000*rxndict['reag3_target_conc_chemical3'])
    aminemassB=(Aminemol*float(chemdf.loc[rxndict['chem3_abbreviation'], "Molecular Weight (g/mol)"]))

    #The following section handles and output dataframes to the format required by the robot.xls file.  File type is very picky about white space and formatting.  
    FinalAmountArray_hold={}
    FinalAmountArray_hold['solvent_volume']=((solventvolume/1000).round(2))
    FinalAmountArray_hold['pbi2mass']=(PbI2mass.round(2))
    FinalAmountArray_hold['Aaminemass']=((aminemassA.round(2)))
    FinalAmountArray_hold['Afinalvolume']=((stockAvolume/1000).round(2))
    FinalAmountArray_hold['Baminemass']=(aminemassB.round(2))
    FinalAmountArray_hold['Bfinalvolume']=((stockBvolume/1000).round(2))
    FinalAmountArray_hold['FA6']=((stockFormicAcid6/1000).round(2))
    FinalAmountArray_hold['FA7']=((stockFormicAcid7/1000).round(2))
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


''' This sort of parsing is needed to ensure that the diversity of experiments that 
we geenrate throughout this process is scalable.  We don't want to be limited on the 
nubmer of reactions that can be considered for a single plate. Lots of things need to
be organized sequentially.  This code is written out long form to make the manipulations 
more interpretable '''
# parse the reaction dictionary and reagent dictionary for information on specific experiment
def expbuild(rxndict, rdict): 
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
    totalexperiments = (len(exp))
    # divide remaining wells not manually assigned for the other experiments, add the well count to exp_wells dict and rxndict for later use.
    rxndict['totalexperiments'] = totalexperiments
    (rxndict, edict) = expwellcount(rxndict, exp, exp_wells, edict)
    # Use the experimental information to create a unique experiemnt for each well based on the general experimental constraints (use class object ot keep track of volumes)
    # Each particular subdivision of wells (each exp grouping) is added to the dictionary of overall experiments and returned
    return(rxndict, edict)



def chemicallimits(rxndict):
    climits = {}
    for k,v in rxndict.items():
        if "chem" in k and "molarmin" in k:
            climits[k] = v
        if "chem" in k and "molarmax" in k:
            climits[k] = v
    return(climits)

# Clean up the final volume dataframe so the robot doesn't die
def postprocess(erdf, maxr):
    columnlist = []
    templatelst = [0]*(len(erdf.iloc[0:]))
    for column in erdf.columns:
        columnlist.append(column)
    count = 1
    newcolumnslist = []
    while count <= maxr:
        reagentname =('Reagent%s (ul)' %count)
        if reagentname not in columnlist:
            newcolumnslist.append(reagentname)
        else:
            pass
        count+=1
    for item in newcolumnslist:
        newdf = pd.DataFrame(templatelst)
        newdf.columns = [item]
        erdf = pd.concat([erdf, newdf], axis=1, sort=True)
    erdf = erdf.reindex(sorted(erdf.columns), axis=1)
    return(erdf)

def augdescriptors(inchikeys, rxndict, erdfrows):
    #bring in the inchi key based features for a left merge
    with open('perov_desc.csv', 'r') as my_descriptors:
       descriptor_df=pd.read_csv(my_descriptors) 
    descriptor_df=inchikeys.merge(descriptor_df, left_on='_rxn_organic-inchikey', right_on='_raw_inchikey', how='inner')
    cur_list = [c for c in descriptor_df.columns if 'raw' not in c]
    descriptor_df = descriptor_df[cur_list]
    descriptor_df.drop(columns=['_rxn_organic-inchikey'], inplace=True)
    ds1 = [rxndict['duratation_stir1']]*erdfrows
    ds1df = pd.DataFrame(ds1, columns=['_rxn_mixingtime1S'])
    ds2 = [rxndict['duratation_stir2']]*erdfrows
    ds2df = pd.DataFrame(ds2, columns=['_rxn_mixingtime2S'])
    dr = [rxndict['duration_reaction']]*erdfrows
    drdf = pd.DataFrame(dr, columns=['_rxn_reactiontimeS'])
    sr1 = [rxndict['stirrate']]*erdfrows
    sr1df = pd.DataFrame(sr1, columns=['_rxn_stirrateRPM'])
    t = [rxndict['temperature2_nominal']]*erdfrows
    tdf = pd.DataFrame(t, columns=['_rxn_temperatureC'])
    outdf = pd.concat([inchikeys, ds1df,ds2df,drdf,sr1df,tdf,descriptor_df], axis=1)
    return(outdf)

## Prepares directory and relevant files, calls upon code to operate on those files to generate a new experimental run (workflow 1)
def datapipeline(rxndict, vardict):
    '''Gathers experimental environment from user (rxndict), dev (vardict), and googleapi for file handling

    '''
    testing.prebuildvalidation(rxndict) # testing to ensure that the user defined parameters match code specs.  
    chemdf=chemical.ChemicalData() #Dataframe containing all of the chemical information from gdrive
    climits = chemicallimits(rxndict) #Dictionary with the user defined chemical limits for later use
    rdict=reagent.buildreagents(rxndict, chemdf)
    for k,v in rdict.items():
        modlog.info("%s : %s" %(k,vars(v)))
    (rxndict, edict)=expbuild(rxndict, rdict) # Send off the experiments to be built using the reagents and the experimental constraints from the rxndict chemicals
    testing.postbuildvalidation(rxndict,rdict,edict) # some basic in line code to make sure that the experiment and reagents have been correctly constructed by the user
    #Send out all of the constraints and chemical information for run assembly (all experiments are returned)
    (erdf, ermmoldf, emsumdf) = rxnprng.preprocess(chemdf, rxndict, edict, rdict, climits) 
    # Clean up dataframe for robot file -> create xls --> upload 
    erdfrows = erdf.shape[0]
    erdf = postprocess(erdf, vardict['max_robot_reagents'])



    from capture.prepare import interface
    # Generate new CP run
    if vardict['challengeproblem'] == 1:
        ermmolcsv = ('localfiles/%s_mmolbreakout.csv' %rxndict['RunID'])
        ermmoldf.to_csv(ermmolcsv)
        emsumcsv = ('localfiles/%s_nominalMolarity.csv' %rxndict['RunID'])
        emsumdf.to_csv(emsumcsv)
        prerun = ('localfiles/%s_prerun.csv' %rxndict['RunID'])
        stateset = ('localfiles/%sstateset.csv' %rxndict['chem3_abbreviation'])
        # Hardcode the inchikey lookup for the "amine" aka chemical 3 for the time being, though there must be a BETTER WAY!
        # Hardcode the inchikey lookup for the "amine" aka chemical 3 for the time being, though there must be a BETTER WAY!
        inchilist = [(chemdf.loc[rxndict['chem3_abbreviation'], "InChI Key (ID)"])]*erdfrows
        inchidf = pd.DataFrame(inchilist, columns=['_rxn_organic-inchikey'])
        #highly specific curation for the wf1 cp dataflow # drops GBL column
        emsumdf.drop(columns=['chemical1 [M]'], inplace=True)
        emsumdf.rename(columns={"chemical2 [M]":"_rxn_M_inorganic", "chemical3 [M]":"_rxn_M_organic", "chemical5 [M]":"_rxn_M_acid"}, inplace=True)
        ddf = augdescriptors(inchidf, rxndict, erdfrows)
        prerun_df = pd.concat([erdf, emsumdf, ddf], axis=1)
        stateset_df = pd.concat([emsumdf,ddf], axis=1)
        #hidden toggle to prevent state space from having all of the features added
#        stateset_df = emsumdf
        prerun_df.to_csv(prerun)
        prerun_df.to_csv(prerun)
        stateset_df.to_csv(stateset)
        uploadlist = [prerun, stateset]
        secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
        if vardict['debug'] == 1:
            pass
        else:
            interface.PrepareDirectoryCP(uploadlist, secfilelist, rxndict['RunID'], rxndict['logfile'],rdict) #Significant online operation, slow.  Comment out to test .xls generation (robot file) portions of the code more quickly
    #Execute normal run
    elif vardict['challengeproblem'] == 0:
        robotfile = preprobotfile(rxndict, vardict, erdf)
        # Export additional information files for later use / storage 
        ermmolcsv = ('localfiles/%s_mmolbreakout.csv' %rxndict['RunID'])
        ermmoldf.to_csv(ermmolcsv)
        emsumcsv = ('localfiles/%s_nominalMolarity.csv' %rxndict['RunID'])
        emsumdf.to_csv(emsumcsv)
        # List to send for uploads 
        uploadlist = [robotfile]
        secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
        prepdict =  conreag(rxndict, erdf, chemdf, rdict, robotfile)
        if vardict['debug'] == 1:
            pass
        else:
            interface.PrepareDirectory(uploadlist, secfilelist, prepdict, rxndict, rdict, vardict) #Significant online operation, slow.  Comment out to test .xls generation (robot file) portions of the code more quickly
    print("Job Creation Complete")
