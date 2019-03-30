#Copyright (c) 2018 Ian Pendleton - MIT License
import os
import logging
import json
import logging
from pandas import ExcelWriter

from capture import testing
from capture.generate import generator
from capture.models import reagent
from capture.models import chemical
from capture.templates import experiment

# create logger
modlog = logging.getLogger('capture.specify')

def specifyexp(test, value):
    expdict = {}
    expdict[test] = "value"
    return(expdict)

## Prepares directory and relevant files, calls upon code to operate on those files to generate a new experimental run (workflow 1)
def datapipeline(rxndict, vardict):
    '''Gathers experimental environment from user (rxndict), dev (vardict), and googleapi for file handling

    '''
    testing.prebuildvalidation(rxndict) # testing to ensure that the user defined parameters match code specs.  
    chemdf=chemical.ChemicalData() #Dataframe containing all of the chemical information from gdrive
    climits = chemical.chemicallimits(rxndict) #Dictionary with the user defined chemical limits for later use
    rdict=reagent.buildreagents(rxndict, chemdf)
    for k,v in rdict.items(): 
        modlog.info("%s : %s" %(k,vars(v)))
    expdict=specifyexp('test', 'value')
    experiment.exppartition_new(rxndict, rdict)
    (rxndict, edict)=experiment.exppartition(rxndict, rdict) # Send off the experiments to be built using the reagents and the experimental constraints from the rxndict chemicals
    for item, value in expdict.items():
        modlog.info("%s,%s" %(item, value))
    testing.postbuildvalidation(rxndict,rdict,edict) # some basic in line code to make sure that the experiment and reagents have been correctly constructed by the user
    #Send out all of the constraints and chemical information for run assembly (all experiments are returned)
    generator.expgen(vardict, chemdf, rxndict, edict, rdict, climits)
    print("Job Creation Complete")