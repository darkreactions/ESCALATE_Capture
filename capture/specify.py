"""

"""
#Copyright (c) 2018 Ian Pendleton - MIT License
import os
import sys
import logging
import json
import logging
from pandas import ExcelWriter

from capture.prepare import reagent_interface as interface
from capture.testing import inputvalidation
from capture.generate import generator
from capture.models import reagent
from capture.models import chemical
from capture.templates import expbuild
from capture.googleapi import googleio


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
    chemdf=chemical.ChemicalData(vardict['chemsheetid'],vardict['chem_workbook_index']) #Dataframe with chemical information from gdrive
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
            uploadlist, secfilelist = generator.CPexpgen(vardict,
                                                         chemdf,
                                                         rxndict,
                                                         edict,
                                                         rdict,
                                                         climits)
            if vardict['debug'] == 1:
                pass
            else:
                #prepare
                interface.PrepareDirectoryCP(uploadlist,
                                             secfilelist,
                                             rxndict['RunID'],
                                             rxndict['logfile'],
                                             rdict,
                                             vardict['targetfolder'])

    #generate
    if vardict['challengeproblem'] == 0:
        #Create experiment file and relevant experiment associated data
        (erdf, robotfile, secfilelist) = generator.expgen(vardict,
                                                          chemdf,
                                                          rxndict,
                                                          edict,
                                                          rdict,
                                                          climits)
        # disable uploading if debug is activated 
        if vardict['debug'] == 1:
            pass
        else:            
            modlog.info('Starting file preparation for upload')
            # Lab specific handling - different labs require different files for tracking
            if rxndict['lab'] == 'LBL' or \
               rxndict['lab'] == "HC" or  \
               rxndict['lab'] == "MIT_PVLab":
                PriDir, secdir, filedict =  \
                    googleio.genddirectories(rxndict,
                                             vardict['targetfolder'],
                                             vardict['filereqs'])
                reagentinterfacetarget, gspreadauth = googleio.gsheettarget(filedict)
                #  abstract experiment data to reagent level (generate reagent preparation based on user requests)

                finalexportdf = interface.reagent_data_prep(rxndict, vardict, erdf, rdict, chemdf)

                sheetobject = interface.reagent_interface_upload(rxndict,
                                                                 vardict,
                                                                 finalexportdf,
                                                                 gspreadauth,
                                                                 reagentinterfacetarget)

                interface.reagent_prep_pipeline(rdict, sheetobject, vardict['max_robot_reagents'])
            elif rxndict['lab'] == "ECL": 
                (PriDir, secdir, filedict) = googleio.genddirectories(rxndict,vardict['targetfolder'], vardict['filereqs'])
                modlog.warn('User selected ECL run, no reagent interface generated.  Please ensure the JSON is exported from ECL!')
                pass
            else:
                modlog.error('User selected a lab that was not supported.  Closing run')
                sys.exit()
            logfile = '%s/%s'%(os.getcwd(),rxndict['logfile'])
            googleio.GupFile(PriDir, secdir, secfilelist, robotfile, \
                rxndict['RunID'], logfile)
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
