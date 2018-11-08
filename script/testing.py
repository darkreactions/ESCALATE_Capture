import sys
import logging



def postbuildvalidation(rxndict,rdict,edict):
    modlog = logging.getLogger('initialize.postbuildvalidation')
#        modlog.error("Fatal error. Reagents and chemicals are over constrained. Recheck user options!")
    print('Experiment successfully constructured.')

def prebuildvalidation(rxndict):
    modlog = logging.getLogger('initialize.prebuildvalidation')
    modlog.info('User entry is configured correctly.  Proceeding with run')

def reagenttesting(volmax, volmin):
    ## Need a chunck of code which elegantly errors if the user sets too many constraints on the chemicals in the experiment
    modlog = logging.getLogger('initialize.reagenttesting')
    if volmax < volmin:
        modlog.error("System is overconstrained!  Please ensure that reasonable limits have been set for chemical limits!")
        sys.exit()
    if volmax == volmin:
        modlog.error("System is overconstrained!  Please ensure that reasonable limits have been set for chemical limits!")
        sys.exit()
    else: modlog.info("Reagent class passes inspection")



### Tests for development
# ensure that the relevant concentrations have been input by the user

#Failsafe check for total volumes
#    maxVol=(rdf1.sum(1).max())
#    if maxVol > rxndict['maximum_total_volume']:
#        print((rdf.loc[:,"Reagent1 (ul)"]+rdf.loc[:,"Reagent2 (ul)"]+rdf.loc[:, "Reagent3 (ul)"]+rdf.loc[:, "Reagent4 (ul)"]+rdf.loc[:, "Reagent5 (ul)"]+rdf.loc[:, "Reagent6 (ul)"]).max())
#        print("ERROR: An incorrect correct configuration has been entered resulting in %suL which exceeds the maximum of %suL of total well volume" %(maxVol, rxndict['maximum_total_volume']))
#        print("    Please correct the configuration and attempt this run again")
#        sys.exit()

# More flags on artificial constraints of total sample collection
# are there reagents in the second portion that are present in the first? Not possible to discriminate yet... (needs to be implemented from the robotic side) 
# does the first chemical of the first reagent constrain the system? not fatal but should be flagged as possible nonsense until coded
 # Need a check to make sure the sizes of the lists in the experimental dict are correct and correspondant.  These are largely automatically generated so the process should be fairly robust
# need a warning which checks final concentrations.  The likely violations will be from instances where the minimum volume increases the overall concentration above some user defined threshold ## This is an "Overconstrain" and just should be an alert
# Noted assumption, use the most concentrated solution to fill to a minimum user requirement