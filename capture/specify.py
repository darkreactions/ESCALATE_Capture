#Copyright (c) 2018 Ian Pendleton - MIT License
import os
import logging
import json
import logging
from pandas import ExcelWriter

from capture.testing import inputvalidation
from capture.generate import generator
from capture.models import reagent
from capture.models import chemical
from capture.templates import expbuild

# create logger
modlog = logging.getLogger('capture.specify')

## Prepares directory and relevant files, calls upon code to operate on those files to generate a new experimental run (workflow 1)
def datapipeline(rxndict, vardict):
    '''Gathers experimental environment from user (rxndict), dev (vardict), and googleapi for file handling

    '''
    inputvalidation.prebuildvalidation(rxndict) # testing to ensure that the user defined parameters match code specs.  
    chemdf=chemical.ChemicalData() #Dataframe containing all of the chemical information from gdrive
    climits = chemical.chemicallimits(rxndict) #Dictionary with the user defined chemical limits for later use
    rdict=reagent.buildreagents(rxndict, chemdf) 
    for k,v in rdict.items(): 
        modlog.info("%s : %s" %(k,vars(v)))
    rxndict['totalexperiments'] = exptotal(rxndict, rdict)
    edict = exppartition(rxndict) 
    inputvalidation.postbuildvalidation(rxndict,rdict,edict) # some basic in line code to make sure that the experiment and reagents have been correctly constructed by the user
    #Send out all of the constraints and chemical information for run assembly (all experiments are returned)
    generator.expgen(vardict, chemdf, rxndict, edict, rdict, climits)
    print("Job Creation Complete")

def exppartition(rxndict): 
    '''  Takes rxndict information and returns a dictionary of experiment templates 
    
    separates each of the specified experiments into individual instances and stores the experiments,
    associated, reagents, chemical information as dictionaries.  Dictionaries are reported to the log file
    '''
    edict = {}
    for k,v in rxndict.items():
        if 'exp' in k:
            edict[k] = v
    for item, value in edict.items():
        modlog.info("%s,%s" %(item, value))
    return(edict)

def exptotal(rxndict, rdict):
    ''' Counts the total number of unique experiment templates specified by the user from the xls interface ''' 
    # pull out only the terms with exp in the name (just consider and manipulate user defined variables) this will break if user adds variables with no default processing, that breaking is intentional
    edict = {}
    for k,v in rxndict.items(): #get out all of the information about experiments (the chemicals and the associated volumes and well counts)
        if 'exp' in k:
            edict[k] = v
    #separate out the experimetnatl informatio nadn the volume information
    expnamelist = []
    for entry,value in edict.items(): #isolate the information about experiments and the volumes, but keep them linked
        if len(entry) == 4:
            expnum = int(entry[-1:])
            expnamelist.append(expnum)
    # Determine how many different xperiments are running on this tray
    totalexperiments = (len(expnamelist))
    return(totalexperiments)

#old code, saving until confirmed that it isn't needed
#def exppartition(rxndict): 
#    '''  Takes rxndict information and returns a dictionary of experiment templates 
#    
#    separates each of the specified experiments into individual instances and stores the experiments,
#    associated, reagents, chemical information as dictionaries.  Dictionaries are reported to the log file
#    '''
#    # pull out only the terms with exp in the name (just consider and manipulate user defined variables) this will break if user adds variables with no default processing, that breaking is intentional
#    edict = {}
#    for k,v in rxndict.items(): #get out all of the information about experiments (the chemicals and the associated volumes and well counts)
#        if 'exp' in k:
#            edict[k] = v
##    exp = {}
##    exp_vols = {}
##    exp_wells = {}
#    #separate out the experimetnatl informatio nadn the volume information
##    for entry,value in edict.items(): #isolate the information about experiments and the volumes, but keep them linked
##        if 'vol' in entry:
##            updatedname = entry.split("_")
##            print(updatedname)
##            exp_vols[updatedname[0]] = value
##        # some code to make sure that manually selected numbers of wells can be parsed and the remaining automatatically divided
##        elif 'wells' in entry:
##            exp_wells[entry] = value
##        else:
##            exp[entry] = value
##    edict = expbuild.expdictbuild(rxndict, exp, exp_wells, edict)
#    return(edict)