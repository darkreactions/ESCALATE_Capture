import pandas as pd
import sys
import logging

from capture.inspect import plotter
from capture.generate import qrandom
from capture.generate import statespace
from capture.prepare import stateset
from capture.prepare import experiment_interface as expint

modlog = logging.getLogger('capture.generate.generator')

def statepipe(vardict, chemdf, rxndict, edict, rdict, volspacing):
    (erdf, ermmoldf, emsumdf) =statespace.statepreprocess(chemdf, rxndict, edict, rdict, volspacing) 
    # Clean up dataframe for robot file -> create xls --> upload 
    erdfrows = erdf.shape[0]
    erdf = expint.cleanvolarray(erdf, vardict['max_robot_reagents'])
    ermmolcsv = ('localfiles/%s_mmolbreakout.csv' %rxndict['RunID'])
    ermmoldf.to_csv(ermmolcsv)
    emsumcsv = ('localfiles/%s_nominalMolarity.csv' %rxndict['RunID'])
    emsumdf.to_csv(emsumcsv)
    statesetfile = ('localfiles/%sstateset.csv' %rdict['2'].chemicals)
    prerun = ('localfiles/%sstateset.link.csv' %rdict['2'].chemicals)
    # Hardcode the inchikey lookup for the "amine" aka chemical 3 for the time being, though there must be a BETTER WAY!
    inchilist = [(chemdf.loc[rdict['2'].chemicals[1], "InChI Key (ID)"])]*erdfrows
    inchidf = pd.DataFrame(inchilist, columns=['_rxn_organic-inchikey'])
    #highly specific curation for the wf1 cp dataflow # drops solvent column
    for chemical in emsumdf.columns:
        chemicalname = chemical.split(' ')[0]
        if chemicalname in vardict['solventlist'] and chemicalname != "FAH":
            solventheader = chemical
    emsumdf.drop(columns=[solventheader], inplace=True)
    emsumdf.rename(columns={"%s [M]"%rdict['2'].chemicals[0]:"_rxn_M_inorganic", \
        "%s [M]"%rdict['2'].chemicals[1]:"_rxn_M_organic", "%s [M]"%rdict['7'].chemicals[0]:"_rxn_M_acid"}, inplace=True)
    modlog.warning("The following chemicals have been assigned generic column names:")
    modlog.warning("%s [M] --> _rxn_M_inorganic" %rdict['2'].chemicals[0])
    modlog.warning("%s [M] --> _rxn_M_organic" %rdict['2'].chemicals[1])
    modlog.warning("%s [M] --> _rxn_M_acid" %rdict['7'].chemicals[0])
    ddf = stateset.augdescriptors(inchidf, rxndict, erdfrows)
    prerun_df = pd.concat([erdf, emsumdf, ddf], axis=1)
    stateset_df = pd.concat([emsumdf,ddf], axis=1)
#    stateset_df = emsumdf #toggle to prevent state space from having all of the features added
    prerun_df.to_csv(prerun)
    stateset_df.to_csv(statesetfile)
    uploadlist = [prerun, statesetfile]
    secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
    return(emsumdf, uploadlist, secfilelist, rdict)

def quasirandompipe(vardict, chemdf, rxndict, edict, rdict, climits):
    (erdf, ermmoldf, emsumdf) = qrandom.preprocess_and_sample(chemdf, rxndict, edict, rdict, climits)
    # Clean up dataframe for robot file -> create xls --> upload 
    erdf = expint.cleanvolarray(erdf, vardict['max_robot_reagents'])
    # Export additional information files for later use / storage 
    ermmolcsv = ('localfiles/%s_mmolbreakout.csv' %rxndict['RunID'])
    ermmoldf.to_csv(ermmolcsv)
    emsumcsv = ('localfiles/%s_nominalMolarity.csv' %rxndict['RunID'])
    emsumdf.to_csv(emsumcsv)
    # List to send for uploads 
    secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
    return(emsumdf, secfilelist, erdf)

def CPexpgen(vardict, chemdf, rxndict, edict, rdict, climits):
    '''Generate stateset and associated files
    '''
    (emsumdf, uploadlist, secfilelist, rdict) = statepipe(vardict, chemdf, rxndict, edict, rdict, vardict['volspacing'])
    if rxndict['plotter_on'] == 1:
        if 1 <= rxndict['ExpWorkflowVer'] < 2:
            plotter.plotmewf1(emsumdf, rxndict)
        else:
            modlog.warning("Plot has been enabled, but no workflow specific plot has been programmed.  Not plot will be shown")
    else:
        pass
    return(uploadlist, secfilelist)    

def expgen(vardict, chemdf, rxndict, edict, rdict, climits):
    '''Generate stateset and associated files
    Generate a random sample run on gdrive
    '''
    (emsumdf, secfilelist, erdf) = quasirandompipe(vardict, chemdf, rxndict, edict, rdict, climits)
    if rxndict['plotter_on'] == 1:
        if 1 <= rxndict['ExpWorkflowVer'] < 2:
            plotter.plotmewf1(emsumdf, rxndict)
        else:
            modlog.warning("Plot has been enabled, but no workflow specific plot has been programmed.  Not plot will be shown")
    else:
        pass

    # Generate a different robot file depending on the user specified lab
    if rxndict['lab'] == 'LBL' or rxndict['lab'] == "HC":
        robotfile = expint.LBLrobotfile(rxndict, vardict, erdf)
    elif rxndict['lab'] == "ECL": 
        robotfile = expint.ECLrobotfile(rxndict, vardict, rdict, erdf)
    else:
        modlog.error('User did not specify a supported lab. No robot file will be generated.')
        sys.exit()
    return(erdf, robotfile, secfilelist)

