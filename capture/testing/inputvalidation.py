import sys
import logging


def expcount(rxndict):
    modlog = logging.getLogger('capture.prebuildvalidation.expcount')
    edict = {}
    for k, v in rxndict.items():
        if 'exp' in k:
            edict[k] = v
    for entry, value in edict.items():
        if len(entry) == 4:
            try:
                expcount = int(entry[-1:])
            except:
                modlog.error('Experiment counts do not end in a number.  Please check the names of variables in the xls experiment category')
                sys.exit()
                pass
        if expcount < 0 and expcount > 10:
            modlog.error("Experiments are improperly numbered.  Please check the names of variables in the xls experiment category")
            sys.exit()
    modlog.info("Experiments correctly named and numbered")

def expwellcount(rxndict):
    ''' Takes user xls specifications for well counts and ensures compatibility with code
    '''
    modlog = logging.getLogger('capture.prebuildvalidation.expcount')
    expwells = []
    expcount=0
    for k,v in rxndict.items():
        if 'exp' in k and len(k) == 4:
            expcount+=1
    for entry, value in rxndict.items():
        if 'exp' in entry and 'well' in entry:
            expwells.append(value)
        else: pass
    fixed_wells = rxndict['fixed_wells'] #this is bad. I don't like having hard_coded this in.
    if (sum(expwells) + fixed_wells > rxndict['wellcount']):
        modlog.error("Experiments requested outnumber allotted wells. Check well counts for each experiment")
        sys.exit()
    elif (sum(expwells) + fixed_wells < rxndict['wellcount']):
        modlog.error("Experiments requested do not sum to the allotted wells. Check well counts for each experiment")
        sys.exit()
    else: pass
    modlog.info("Only 1 experiment specified. Wellcount applies to only experiment")

def userinterface(rxndict):
    assert isinstance(rxndict['exp1'], list), 'exp1 in user XLS must be specified as a list of lists'

def reagconcdefs(rxndict):
    for k,v in rxndict.items():
        pass

def postbuildvalidation(rxndict,rdict,edict):
    modlog = logging.getLogger('capture.postbuildvalidation')
#        modlog.error("Fatal error. Reagents and chemicals are over constrained. Recheck user options!")
    modlog.info('Experiment successfully constructed.')

def prebuildvalidation(rxndict):
    '''handles validation functions for xls input file

    takes the rxndict as input and performs validation on the input to ensure the proper structure
    -- currently underdeveloped
    '''
    modlog = logging.getLogger('capture.prebuildvalidation')
    userinterface(rxndict)
    expcount(rxndict)
    expwellcount(rxndict)
    reagconcdefs(rxndict)
    modlog.info('User entry is configured correctly.  Proceeding with run')

def reagenttesting(volmax, volmin):
    ## Need a chunck of code which elegantly errors if the user sets too many constraints on the chemicals in the experiment
    modlog = logging.getLogger('capture.reagenttesting')
    if volmax < volmin:
        modlog.error("System is overconstrained!  Please ensure that reasonable limits have been set for chemical limits!")
        sys.exit()
    if volmax == volmin:
        modlog.error("System is overconstrained!  Please ensure that reasonable limits have been set for chemical limits!")
        sys.exit()
    else: modlog.info("Reagent class passes inspection")

# More flags on artificial constraints of total sample collection
# are there reagents in the second portion that are present in the first? Not possible to discriminate yet... (needs to be implemented from the robotic side) 
# does the first chemical of the first reagent constrain the system? not fatal but should be flagged as possible nonsense until coded
 # Need a check to make sure the sizes of the lists in the experimental dict are correct and correspondant.  These are largely automatically generated so the process should be fairly robust
# need a warning which checks final concentrations.  The likely violations will be from instances where the minimum volume increases the overall concentration above some user defined threshold ## This is an "Overconstrain" and just should be an alert
# Noted assumption, use the most concentrated solution to fill to a minimum user requirement