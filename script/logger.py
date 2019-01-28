import logging
from datetime import datetime, timezone

from shutil import copyfile

def buildlogger(rxndict):
    # create logger with 'initialize'
    logger = logging.getLogger('initialize')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs event debug messages
    fh = logging.FileHandler('localfiles/%s_LogFile.log' %rxndict['RunID'])
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
    return('localfiles/%s_Logfile.log' %rxndict['RunID'])

def runuidgen(rxndict):
    rxndict['readdate_gen']=datetime.now(timezone.utc).isoformat()
    rxndict['readdate']=rxndict['readdate_gen'].replace(':', '_') #Remove problematic characters
    rxndict['date']=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rxndict['time']=datetime.now(timezone.utc).strftime("%H_%M_%S")
    rxndict['RunID']=rxndict['readdate'] + "_" + rxndict['lab'] #Agreed Upon format for final run information
    copyfile(rxndict['exefilename'], 'localfiles/%s_%s' %(rxndict['RunID'], rxndict['exefilename']))
    rxndict['exefilename'] = 'localfiles/%s_%s' %(rxndict['RunID'], rxndict['exefilename'])
    return(rxndict)

# A bit of automation in curating the chemical space.  Sanity checked value will be output to the final log
#def cleanvalues(rxndict):
#    modlog = logging.getLogger('initialize.cleanvalues')
#    try: # ensures that the maximum concentration of chemical 2 does not exceed the upper physical limitation (should be done for each chemical eventually)
#        if rxndict['chem2_molarmax'] > rxndict['reag2_target_conc_chemical2']*rxndict['reagent_target_volume']/1000:
#            rxndict['chem2_molarmax']=rxndict['reag2_target_conc_chemical2']*rxndict['reagent_target_volume']/1000
#            modlog.warning("Maximum mmol target for %s set too high - adjusted to %s mmol" %(rxndict['chem2_abbreviation'],rxndict['chem2_max']))
#        else:
#            rxndict['chem2_molarmax']
#            pass
#    except KeyError:
#        rxndict['chem2_molarmax']=rxndict['reag2_target_conc_chemical2']*rxndict['reagent_target_volume']/1000
#        rxndict['chem2_molarmax']
#    return(rxndict)

#record a detailed and organized set of the variables set by the user
def initialize(rxndict):
    modlog = logging.getLogger('initialize.variablelogging')
    #Adjust for manual setting perovskite workflow 1 specific
    ##Setup Run ID Information
    modlog.info("Plotted (? -- boolean) = %s " %rxndict['plotter_on'])
    #Plate variables
    modlog.info("Pre-reaction Temperature = %s:celsius" %rxndict['temperature1_nominal'])
    modlog.info("Tray Shake Rate 1 (After First Addition) = %s:RPM" %rxndict['duratation_stir1'])
    modlog.info("Tray Shake Rate 2 (After FAH addition) = %s:RPM" %rxndict['duratation_stir2'])
    modlog.info("Reaction Temperature of Tray = %s:celsius" %rxndict['temperature2_nominal'])
    modlog.info("Duration held at final temperature = %s:second" %rxndict['duration_reaction'])
    modlog.info("Wellcount %s" %rxndict['wellcount'])
    # Reagent variables
    modlog.info("reagents preparation temperature = %s Celsius" %rxndict['reagents_prep_temperature'])
    modlog.info("reagents preparation stir rate = %s RPM" %rxndict['reagents_prep_stirrate'])
    modlog.info("reagents preparation duration = %s seconds" %rxndict['reagents_prep_duration'])
    modlog.info("reag2_target_conc_chemical2 = %s M" %rxndict['reag2_target_conc_chemical2'])
    modlog.info("reag2_target_conc_chemical3 = %s M" %rxndict['reag2_target_conc_chemical3'])
    modlog.info("reag3_target_conc_chemical2 = %s M" %rxndict['reag3_target_conc_chemical3'])
    modlog.info("reagents_prerxn_temperature = %s Celsius" %rxndict['reagents_prerxn_temperature'])
    modlog.info("reagent_dead_volume = %s:mL" %rxndict['reagent_dead_volume'])
#    modlog.info("reagent 1,2,3 target volume = %s:mL" %rxndict['reagent_target_volume'])
#    modlog.info("reagent maximum volume threshold = %s:mL" %rxndict['maximum_total_volume'])
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