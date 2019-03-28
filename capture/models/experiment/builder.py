import sys
import logging

modlog = logging.getLogger('capture.models.experiment.builder')

def expwellcount(rxndict, exp, exp_wells,edict):
    # if already configured with all well counts explicityly defined, return an unaltered well count dict
    # else do some checks on the manual entry and add specific well count values where appropriate
    # assumes that any well count values not explicitly defined will be divided amongst the non-defined experiments
    basewellcount = []
    expwithwells = []
    # Calculates how many experimental wells have been manually assigned
    for k,v in exp_wells.items():
        basewellcount.append(v)
        expwithwells.append(k.split('_')[0])
    forremaining = (rxndict['wellcount'] - sum(basewellcount))
    # If the number of wells being manually specified exceeds the tray limit (user defined), exit.
    if (sum(basewellcount)) > rxndict['wellcount']:
        modlog.error("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
        print("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
        sys.exit()
    # ensures that the total number of wells targeted for the tray is correctly specified. Too few wells specified means the user isn't paying attention!
    elif len(exp) == len(exp_wells):
        if (sum(basewellcount)) < rxndict['wellcount']:
            print(forremaining, 'wells remain unallocated. Please check settings')
        else:
            pass
    # Divide up remaining wells and assign appropriately
    else:
        if (sum(basewellcount)) > rxndict['wellcount']:
            modlog.error("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
            print("Fatal error!  Manually entered well count is configured incorrectly! Terminating run")
            sys.exit()
        else: 
            addwellexplist = []
            for experiment,reagents in exp.items():
                if experiment in expwithwells:
                    pass
                else:
                    addwellexplist.append(experiment+'_wells')
            wellsdivided = (forremaining / len(addwellexplist))
            for entry in addwellexplist:
                rxndict[entry] = wellsdivided
                edict[entry] = wellsdivided
    print("Wells for experiments successfully implemented")
    return(rxndict, edict)


''' This sort of parsing is needed to ensure that the diversity of experiments that 
we geenrate throughout this process is scalable.  We don't want to be limited on the 
nubmer of reactions that can be considered for a single plate. Lots of things need to
be organized sequentially.  This code is written out long form to make the manipulations 
more interpretable '''
# parse the reaction dictionary and reagent dictionary for information on specific experiment
def expbuild(rxndict, rdict): 
    # pull out only the terms with exp in the name (just consider and manipulate user defined variables) this will break if user adds variables with no default processing, that breaking is intentional
    edict = {}
    for k,v in rxndict.items(): #get out all of the information about experiments (the chemicals and the associated volumes and well counts)
        if 'exp' in k:
            edict[k] = v
    exp = {}
    exp_vols = {}
    exp_wells = {}
    #separate out the experimetnatl informatio nadn the volume information
    for entry,value in edict.items(): #isolate the information about experiments and the volumes, but keep them linked
        if 'vol' in entry:
            updatedname = entry.split("_")
            exp_vols[updatedname[0]] = value
        # some code to make sure that manually selected numbers of wells can be parsed and the remaining automatatically divided
        elif 'wells' in entry:
            exp_wells[entry] = value
        else:
            exp[entry] = value
    # Determine how many different xperiments are running on this tray
    totalexperiments = (len(exp))
    # divide remaining wells not manually assigned for the other experiments, add the well count to exp_wells dict and rxndict for later use.
    rxndict['totalexperiments'] = totalexperiments
    (rxndict, edict) = expwellcount(rxndict, exp, exp_wells, edict)
    # Use the experimental information to create a unique experiemnt for each well based on the general experimental constraints (use class object ot keep track of volumes)
    # Each particular subdivision of wells (each exp grouping) is added to the dictionary of overall experiments and returned
    return(rxndict, edict)