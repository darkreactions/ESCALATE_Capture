import os
import logging
from datetime import datetime, timezone
from shutil import copyfile

def buildlogger(rxndict):
    # create logger with 'initialize'
    logger = logging.getLogger('capture')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs event debug messages
    logfile = '%s/localfiles/%s_LogFile.log' %(os.getcwd(),rxndict['RunID'])
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    wh = logging.StreamHandler()
    wh.setLevel(logging.WARN)
    # create error formatter with the highest log level
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s> %(name)s ; %(levelname)s - %(message)s')
    warning_formatter = logging.Formatter('%(asctime)s> %(name)s ; %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    wh.setFormatter(warning_formatter)
    logger.addHandler(fh)
    logger.addHandler(wh) 
    logger.info('initializing run')
    logger.info("Run Initiation (iso): %s" %rxndict['readdate'])  #Agreed Upon format for final run information
    return('localfiles/%s_LogFile.log' %rxndict['RunID'])

def runuidgen(rxndict, vardict):
    '''generates a UID for the run as needed
    '''
    rxndict['readdate_gen']=datetime.now(timezone.utc).isoformat()
    rxndict['readdate']=rxndict['readdate_gen'].replace(':', '_') #Remove problematic characters
    rxndict['date']=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rxndict['time']=datetime.now(timezone.utc).strftime("%H_%M_%S")
    rxndict['RunID']=rxndict['readdate'] + "_" + rxndict['lab'] #Agreed Upon format for final run information
    copyfile(vardict['exefilename'], 'localfiles/%s_%s' %(rxndict['RunID'], vardict['exefilename']))
    vardict['exefilename'] = 'localfiles/%s_%s' %(rxndict['RunID'], vardict['exefilename'])
    return(rxndict, vardict)

def initialize(rxndict, vardict):
    ''' record a detailed and organized set of the variables set by the user

    also records variables in the vardict space (vardict) variable
    '''
    modlog = logging.getLogger('capture.rxndict')
    modlog.info("USER INPUT VARIABLES (UIV -- key : value in rxndict)")
    for variable, condition in rxndict.items():
        modlog.info("(UIV) %s : %s " %(variable, condition))
    modlog.info("END -- USER INPUT VARIABLES (UIV)")
    modlog = logging.getLogger('capture.vardict')
    modlog.info("DEV INPUT VARIABLES (DIV -- key : value in vardict)")
    for variable, condition in vardict.items():
        modlog.info("(DIV) %s : %s"%(variable, condition))
    modlog.info("END -- DEV INPUT VARIABLES (DIV -- key : value in vardict)")
    ##Space constraints
    for key, value in rxndict.items():
        try: 
            if 'chem' in key and "abbreviation" in key:
                abbreviation = key
            if "chem" in key and "molarmin" in key:
                minimum = key
            if "chem" in key and "molarmax" in key:
                maximum = key
            modlog.info("%s manually set to maximum molarity [%s] and minimum [%s]" %(rxndict[abbreviation],rxndict[maximum],(rxndict[minimum])))
            del(abbreviation, minimum, maximum)
        except:
            pass