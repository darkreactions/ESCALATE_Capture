"""

"""
#Copyright (c) 2018 Ian Pendleton - MIT License
import os
import sys
import logging
import json
import logging
from pandas import ExcelWriter

import capture.googleapi.googleio
from capture.prepare import reagent_interface as interface
from capture.prepare.observation_interface import upload_observation_interface_data
from capture.prepare.observation_interface import upload_modelinfo_observation_interface
from capture.testing import inputvalidation
from capture.generate import generator
from capture.models import reagent
from capture.models import chemical
from capture.templates import expbuild
from capture.googleapi import googleio
import capture.devconfig as config
from utils import globals
from utils.globals import lab_safeget

# create logger
modlog = logging.getLogger('capture.specify')


def datapipeline(rxndict, vardict):
    """Main data pipeline for organizing ESCALATE functionality

    :param rxndict: mostly experiment Template info, see DataStructures_README.md
    :param vardict: mostly command line parameters and devconfig info, see DataStructures_README.md

    Retrieves chemical info from google drive
    Sends Template to state-space generator or random sample generator as specified on command line.
    Saves experiments as csvs and uploads to google drive (if debug is not active)
    """

    modlog = logging.getLogger('capture.specify.datapipeline')
    inputvalidation.prebuildvalidation(rxndict, vardict)

    chemdf = chemical.build_chemdf(lab_safeget(config.lab_vars, globals.get_lab(), 'chemsheetid'),
                                   lab_safeget(config.lab_vars, globals.get_lab(), 'chem_workbook_index'),
                                   vardict['debug'])

    reagentdf = reagent.build_reagentdf(lab_safeget(config.lab_vars, globals.get_lab(),'reagentsheetid'),
                                        lab_safeget(config.lab_vars, globals.get_lab(),'reagent_workbook_index'),
                                        vardict['debug'])

    vardict['solventlist'] = chemdf.index[chemdf['Chemical Category'] == 'solvent'].values.tolist()

    # dictionary of user defined chemical limits
    climits = chemical.chemicallimits(rxndict)

    # dictionary of perovskitereagent objects
    rdict, old_reagents = reagent.buildreagents(rxndict, chemdf, reagentdf, vardict['solventlist'])
    rxndict['totalexperiments'] = exptotal(rxndict, rdict)

    # dictionary of experiments
    edict = exppartition(rxndict)

    drive_target_folder = lab_safeget(config.lab_vars, globals.get_lab(), 'newrun_remote_folder')

    inputvalidation.postbuildvalidation(rxndict, vardict, rdict, edict, chemdf)
    #generate
    if vardict['challengeproblem'] == 1:
        if rxndict['totalexperiments'] > 1:
            modlog.error('Only 1 experiment for stateset generation is supported,\
                user selected %s experiments.' % rxndict['totalexperiments'])
            sys.exit()
        else:
            uploadlist, secfilelist = generator.generate_cp_files(vardict,
                                                                  chemdf,
                                                                  rxndict,
                                                                  edict,
                                                                  rdict,
                                                                  climits)
            if vardict['debug'] is False:
                googleio.upload_cp_files_to_drive(uploadlist,
                                                  secfilelist,
                                                  rxndict['RunID'],
                                                  rxndict['logfile'],
                                                  drive_target_folder)

    # generate
    if not vardict['challengeproblem']:
        # Create experiment file and relevant experiment associated data
        erdf, robotfile, secfilelist, model_info_df = generator.generate_ESCALATE_run(vardict,
                                                                                      chemdf,
                                                                                      rxndict,
                                                                                      edict,
                                                                                      rdict,
                                                                                      old_reagents,
                                                                                      climits)
        if vardict['debug'] < 2:
            modlog.info('Starting file preparation for upload')
            # Lab specific handling - different labs require different files for tracking

            primary_dir, secondary_dir, gdrive_uid_dict = googleio.create_drive_directories(rxndict,
                                                                                            drive_target_folder,
                                                                                            lab_safeget(config.lab_vars, globals.get_lab(),'required_files'))
            if rxndict['lab'] != 'ECL':

                google_drive_client = googleio.get_gdrive_client()

                # upload reagent preparation_interface
                reagent_interface_uid = googleio.get_uid_by_name(
                                        gdrive_uid_dict,
                                        '(ExpDataEntry|preparation_interface)')
                regent_spec_df = interface.build_reagent_spec_df(
                                 rxndict,
                                 vardict,
                                 erdf,
                                 rdict,
                                 chemdf)
                interface.upload_reagent_interface(rxndict,
                                                   vardict,
                                                   rdict,
                                                   regent_spec_df,
                                                   google_drive_client,
                                                   reagent_interface_uid)
                # upload data to observation_interace
                observation_interface_uid = googleio.get_uid_by_name(
                                            gdrive_uid_dict,
                                            'observation_interface')
                upload_observation_interface_data(rxndict,
                                                  vardict,
                                                  google_drive_client,
                                                  observation_interface_uid)
                upload_modelinfo_observation_interface(model_info_df,
                                                       google_drive_client,
                                                       observation_interface_uid)

            else:
                modlog.warn('User selected ECL run, no reagent interface generated. Please ensure the JSON is exported from ECL!')
            logfile = '%s/%s'%(os.getcwd(),rxndict['logfile'])
            googleio.upload_files_to_gdrive(primary_dir, secondary_dir, secfilelist, robotfile, rxndict['RunID'], logfile)
            modlog.info('File upload completed successfully')
        else:
            modlog.info('Offline debugging enabled.  No file upload was performed')
            print('Offline debugging enabled.  No file upload was performed')
    modlog.info("Job Creation Complete")
    print("Job Creation Complete")

def exppartition(rxndict): 
    """Takes rxndict information and returns a dictionary of experiment templates
    
    separates each of the specified experiments into individual instances and 
    stores the experiments, associated, reagents, chemical information as 
    dictionaries.  Dictionaries are reported to the log file
    """
    edict = {}
    for k,v in rxndict.items():
        if 'exp' in k:
            edict[k] = v
    for item, value in edict.items():
        modlog.info("%s,%s" %(item, value))
    return(edict)

def exptotal(rxndict, rdict):
    """Counts total number of experiment templates specified by the xls interface

    pull out only the terms with exp in the name (just consider and manipulate 
    user defined variables) this will break if user adds variables with no default 
    processing 
    """
    edict = {}

    # grab all of the information about experiments from rxndict (input XLS)
    for k, v in rxndict.items():
        if 'exp' in k:
            edict[k] = v
    # grab only exp identifiers from edict
    expnamelist = []
    for entry, value in edict.items():
        if len(entry) == 4:
            expnum = int(entry[-1:])
            expnamelist.append(expnum)  # todo is this why we only support 9 experiments?
    totalexperiments = (len(expnamelist))
    return(totalexperiments)
