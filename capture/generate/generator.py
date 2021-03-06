"""Generator: handles generating experiments

Pipe functions route generation to the statespace or qrandom as apporpriate
"""

import pandas as pd
import sys
import logging

#from capture.inspect import plotter
from capture.generate import qrandom
from capture.generate import statespace
from capture.prepare import stateset
from capture.prepare import experiment_interface as expint
import capture.devconfig as config
from utils.data_handling import abstract_reagent_colnames
from utils import globals
from utils.globals import lab_safeget

modlog = logging.getLogger('capture.generate.generator')

####################################
## STATE SPACE GENERATION FUNCTIONS

def generate_cp_files(vardict, chemdf, rxndict, edict, rdict, climits):
    """Wrapper to statepipe
    """
    emsumdf, uploadlist, secfilelist, rdict = stateset_generation_pipeline(vardict,
                                                                           chemdf,
                                                                           rxndict,
                                                                           edict,
                                                                           rdict,
                                                                           config.volspacing) 

    # TODO: Fix plotting
    # if rxndict['plotter_on'] == 1:
    #     if 1 <= rxndict['ExpWorkflowVer'] < 2:
    #         plotter.plotmewf1(emsumdf, rxndict)
    #     else:
    #         modlog.warning("Plot has been enabled, but no workflow specific plot has been programmed.  Not plot will be shown")
    return uploadlist, secfilelist

def stateset_generation_pipeline(vardict, chemdf, rxndict, edict, rdict, volspacing):
    """Generate stateset and associated files
    """
    erdf, ermmoldf, emsumdf = statespace.preprocess_and_enumerate(chemdf,
                                                                  rxndict,
                                                                  edict,
                                                                  rdict,
                                                                  volspacing)

    # Clean up dataframe for robot file -> create xls --> upload
    erdfrows = erdf.shape[0]
    erdf = expint.cleanvolarray(erdf, lab_safeget(config.lab_vars, globals.get_lab(),'max_reagents'))
    abstract_reagent_colnames(erdf)

    ermmolcsv = 'localfiles/%s_mmolbreakout.csv' % rxndict['RunID']
    abstract_reagent_colnames(ermmoldf)
    ermmoldf.to_csv(ermmolcsv)

    # has no reagent names
    emsumcsv = 'localfiles/%s_nominalMolarity.csv' % rxndict['RunID']
    emsumdf.to_csv(emsumcsv)

    statesetfile = 'localfiles/%sstateset.csv' % rdict['2'].chemicals
    prerun = 'localfiles/%sstateset.link.csv' % rdict['2'].chemicals

    # Hardcode the inchikey lookup for the "amine" aka chemical 3 for the time being, though there must be a BETTER WAY!
    inchilist = [(chemdf.loc[rdict['2'].chemicals[1], "InChI Key (ID)"])]*erdfrows
    inchidf = pd.DataFrame(inchilist, columns=['_rxn_organic-inchikey'])

    #highly specific curation for the wf1 cp dataflow # drops solvent column
    for chemical in emsumdf.columns:
        chemicalname = chemical.split(' ')[0]
        if chemicalname in vardict['solventlist'] and chemicalname != "FAH":
            solventheader = chemical

    emsumdf.drop(columns=[solventheader], inplace=True)
    emsumdf.rename(columns={"%s [M]" % rdict['2'].chemicals[0]: "_rxn_M_inorganic",
                            "%s [M]" % rdict['2'].chemicals[1]: "_rxn_M_organic",
                            "%s [M]" % rdict['7'].chemicals[0]: "_rxn_M_acid"}, inplace=True)

    modlog.warning("The following chemicals have been assigned generic column names:")
    modlog.warning("%s [M] --> _rxn_M_inorganic" % rdict['2'].chemicals[0])
    modlog.warning("%s [M] --> _rxn_M_organic" % rdict['2'].chemicals[1])
    modlog.warning("%s [M] --> _rxn_M_acid" % rdict['7'].chemicals[0])

    ddf = stateset.augdescriptors(inchidf, rxndict, erdfrows)
    prerun_df = pd.concat([erdf, emsumdf, ddf], axis=1)
    stateset_df = pd.concat([emsumdf,ddf], axis=1)
    # stateset_df = emsumdf #toggle to prevent state space from having all of the features added # todo ??
    prerun_df.to_csv(prerun)
    stateset_df.to_csv(statesetfile)

    uploadlist = [prerun, statesetfile]
    secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
    return emsumdf, uploadlist, secfilelist, rdict


####################################
## QUASI RANDOM GENERATION FUNCTIONS


def quasirandom_generation_pipeline(vardict, chemdf, rxndict, edict, rdict, old_reagents, climits):
    """

    TODO: Document rdict
    :param vardict: dictionary built from devconfig
    :param chemdf: chemical dataframe with descriptions of all chemicals in the reaction
    :param rxndict: complete key-value pairing from specification interface (front end xlsx as of 2.56)
    :param edict: dictionary of experiments (see documentation)
    :param rdict: dictionary of reagents defining the concentration space to be sampled.  (see documentation)
    :param old_reagents: dictionary of reagents to subtract from statespace (same structure as rdict)
    :param climits:
    :return:
    """
    erdf, ermmoldf, emsumdf, model_info_df = qrandom.preprocess_and_sample(chemdf,
                                                                           vardict,
                                                                           rxndict,
                                                                           edict,
                                                                           rdict,
                                                                           old_reagents,
                                                                           climits)
    # Clean up dataframe for robot file -> create xls --> upload
    erdf = expint.cleanvolarray(erdf, maxr=lab_safeget(config.lab_vars, globals.get_lab(),'max_reagents'))

    # Export additional information files for later use / storage 
    ermmolcsv = ('localfiles/%s_mmolbreakout.csv' %rxndict['RunID'])
    abstract_reagent_colnames(ermmoldf)
    ermmoldf.to_csv(ermmolcsv)
    emsumcsv = ('localfiles/%s_nominalMolarity.csv' %rxndict['RunID'])
    emsumdf.to_csv(emsumcsv)
    # List to send for uploads
    secfilelist = [ermmolcsv, emsumcsv, vardict['exefilename']]
    return emsumdf, secfilelist, erdf, model_info_df


def generate_ESCALATE_run(vardict, chemdf, rxndict, edict, rdict, old_reagents, climits):
    """Wrapper to quasirandompipe
    """
    emsumdf, secfilelist, erdf, model_info_df = quasirandom_generation_pipeline(vardict,
                                                                                chemdf,
                                                                                rxndict,
                                                                                edict,
                                                                                rdict,
                                                                                old_reagents,
                                                                                climits)

    # TODO fix plotter
    # if rxndict['plotter_on'] == 1:
    #     if 1 <= rxndict['ExpWorkflowVer'] < 2:
    #         plotter.plotmewf1(emsumdf, rxndict)
    #     else:
    #         modlog.warning("Plot has been enabled, but no workflow specific plot has been programmed.  Not plot will be shown")

    # TODO this is brittle
    if rxndict['lab'] == "ECL":
        robotfile = expint.ECLrobotfile(rxndict, vardict, rdict, erdf)
    else:
        robotfile = expint.LBLrobotfile(rxndict, vardict, erdf)
    return erdf, robotfile, secfilelist, model_info_df