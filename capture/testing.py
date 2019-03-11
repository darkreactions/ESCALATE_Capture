import sys
import logging



def postbuildvalidation(rxndict,rdict,edict):
    modlog = logging.getLogger('capture.postbuildvalidation')
#        modlog.error("Fatal error. Reagents and chemicals are over constrained. Recheck user options!")
    print('Experiment successfully constructured.')

def prebuildvalidation(rxndict):
    modlog = logging.getLogger('capture.prebuildvalidation')
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