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
from capture.testing import inputvalidation
from capture.generate import generator
from capture.models import reagent
from capture.models import chemical
from capture.templates import expbuild
from capture.googleapi import googleio
import capture.devconfig as config


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
    chemdf = chemical.ChemicalData(vardict['chemsheetid'], vardict['chem_workbook_index'])
    reagentdf = reagent.ReagentData(vardict['reagentsheetid'], vardict['reagent_workbook_index'])

    # dictionary of user defined chemical limits
    climits = chemical.chemicallimits(rxndict)

    # dictionary of perovskitereagent objects
    rdict = reagent.buildreagents(rxndict, chemdf, reagentdf, vardict['solventlist'])
    rxndict['totalexperiments'] = exptotal(rxndict, rdict)

    # dictionary of experiments
    edict = exppartition(rxndict)

    inputvalidation.postbuildvalidation(rxndict, rdict, edict)
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
            if not vardict['debug']:
                #prepare
                googleio.upload_cp_files_to_drive(uploadlist,
                                                  secfilelist,
                                                  rxndict['RunID'],
                                                  rxndict['logfile'],
                                                  rdict,
                                                  vardict['targetfolder'])

    # generate
    if not vardict['challengeproblem']:
        # Create experiment file and relevant experiment associated data
        erdf, robotfile, secfilelist = generator.generate_ESCALATE_run(vardict,
                                                                       chemdf,
                                                                       rxndict,
                                                                       edict,
                                                                       rdict,
                                                                       climits)
        # disable uploading if debug is activated
        if not vardict['debug']:
            modlog.info('Starting file preparation for upload')
            # Lab specific handling - different labs require different files for tracking

            if not rxndict['lab'] in config.SUPPORTED_LABS:
                modlog.error('User selected a lab that was not supported. Closing run')
                sys.exit()

            primary_dir, secondary_dir, gdrive_uid_dict = googleio.create_drive_directories(rxndict,
                                                                                            vardict['targetfolder'],
                                                                                            vardict['filereqs'])
            if rxndict['lab'] in ['LBL', 'HC', 'MIT_PVLab']:

                google_drive_client = googleio.get_gdrive_client()

                # upload reagent interface
                reagent_interface_uid = googleio.get_reagent_interface_uid(gdrive_uid_dict)
                regent_spec_df = interface.build_reagent_spec_df(rxndict, vardict, erdf, rdict, chemdf)
                interface.upload_reagent_interface(rxndict, vardict, rdict,
                                                   regent_spec_df, google_drive_client, reagent_interface_uid)
            elif rxndict['lab'] == "ECL":
                modlog.warn('User selected ECL run, no reagent interface generated. Please ensure the JSON is exported from ECL!')
            logfile = '%s/%s'%(os.getcwd(),rxndict['logfile'])
            googleio.upload_files_to_gdrive(primary_dir, secondary_dir, secfilelist, robotfile, rxndict['RunID'], logfile)
            modlog.info('File upload completed successfully')
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
