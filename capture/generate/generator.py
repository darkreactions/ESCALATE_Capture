import pandas as pd

from capture.prepare import interface
from capture import rxnprng
from capture.prepare import stateset
from capture.models.experiment import expmodel


def statepipeline(vardict, chemdf, rxndict, edict, rdict, climits):
    (erdf, ermmoldf, emsumdf) = rxnprng.statepreprocess(chemdf, rxndict, edict, rdict, climits) 
    # Clean up dataframe for robot file -> create xls --> upload 
    erdfrows = erdf.shape[0]
    erdf = expmodel.postprocess(erdf, vardict['max_robot_reagents'])
    ermmolcsv = ('localfiles/%s_mmolbreakout.csv' %rxndict['RunID'])
    ermmoldf.to_csv(ermmolcsv)
    emsumcsv = ('localfiles/%s_nominalMolarity.csv' %rxndict['RunID'])
    emsumdf.to_csv(emsumcsv)
    prerun = ('localfiles/%s_prerun.csv' %rxndict['RunID'])
    statesetfile = ('localfiles/%sstateset.csv' %rxndict['chem3_abbreviation'])
    # Hardcode the inchikey lookup for the "amine" aka chemical 3 for the time being, though there must be a BETTER WAY!
    # Hardcode the inchikey lookup for the "amine" aka chemical 3 for the time being, though there must be a BETTER WAY!
    inchilist = [(chemdf.loc[rxndict['chem3_abbreviation'], "InChI Key (ID)"])]*erdfrows
    inchidf = pd.DataFrame(inchilist, columns=['_rxn_organic-inchikey'])
    #highly specific curation for the wf1 cp dataflow # drops GBL column
    emsumdf.drop(columns=['chemical1 [M]'], inplace=True)
    emsumdf.rename(columns={"chemical2 [M]":"_rxn_M_inorganic", "chemical3 [M]":"_rxn_M_organic", "chemical5 [M]":"_rxn_M_acid"}, inplace=True)
    ddf = stateset.augdescriptors(inchidf, rxndict, erdfrows)
    prerun_df = pd.concat([erdf, emsumdf, ddf], axis=1)
    stateset_df = pd.concat([emsumdf,ddf], axis=1)
    #hidden toggle to prevent state space from having all of the features added
#    stateset_df = emsumdf
    prerun_df.to_csv(prerun)
    prerun_df.to_csv(prerun)
    stateset_df.to_csv(statesetfile)
    uploadlist = [prerun, statesetfile]
    secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
    if vardict['debug'] == 1:
        pass
    else:
        interface.PrepareDirectoryCP(uploadlist, secfilelist, rxndict['RunID'], rxndict['logfile'],rdict)

def quasirandom(vardict, chemdf, rxndict, edict, rdict, climits):
    (erdf, ermmoldf, emsumdf) = rxnprng.preprocess(chemdf, rxndict, edict, rdict, climits) 
    # Clean up dataframe for robot file -> create xls --> upload 
    erdfrows = erdf.shape[0]
    erdf = expmodel.postprocess(erdf, vardict['max_robot_reagents'])
    robotfile = expmodel.preprobotfile(rxndict, vardict, erdf)
    # Export additional information files for later use / storage 
    ermmolcsv = ('localfiles/%s_mmolbreakout.csv' %rxndict['RunID'])
    ermmoldf.to_csv(ermmolcsv)
    emsumcsv = ('localfiles/%s_nominalMolarity.csv' %rxndict['RunID'])
    emsumdf.to_csv(emsumcsv)
    # List to send for uploads 
    uploadlist = [robotfile]
    secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
    prepdict =  expmodel.conreag(rxndict, erdf, chemdf, rdict, robotfile)
    if vardict['debug'] == 1:
        pass
    else:
        interface.PrepareDirectory(uploadlist, secfilelist, prepdict, rxndict, rdict, vardict) 

def expgen(vardict, chemdf, rxndict, edict, rdict, climits):
    # Generate new CP run
    if vardict['challengeproblem'] == 1:
        statepipeline(vardict, chemdf, rxndict, edict, rdict, climits)
    #Execute normal run
    elif vardict['challengeproblem'] == 0:
        quasirandom(vardict, chemdf, rxndict, edict, rdict, climits)
        