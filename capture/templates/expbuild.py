import sys
import logging

modlog = logging.getLogger('capture.models.experiment.builder')

#def expdictbuild(rxndict, exp, exp_wells,edict):
#    # if already configured with all well counts explicityly defined, return an unaltered well count dict
#    # else do some checks on the manual entry and add specific well count values where appropriate
#    # assumes that any well count values not explicitly defined will be divided amongst the non-defined experiments
#    basewellcount = []
#    expwithwells = []
#    # Calculates how many experimental wells have been manually assigned
#    for k,v in exp_wells.items():
#        basewellcount.append(v)
#        expwithwells.append(k.split('_')[0])
#    forremaining = (rxndict['wellcount'] - sum(basewellcount))
#    # ensures that the total number of wells targeted for the tray is correctly specified. Too few wells specified means the user isn't paying attention!
#    addwellexplist = []
#    for experiment,reagents in exp.items():
#        if experiment in expwithwells:
#            pass
#        else:
#            addwellexplist.append(experiment+'_wells')
#    wellsdivided = (forremaining / len(addwellexplist))
#    for entry in addwellexplist:
##        rxndict[entry] = wellsdivided
#        edict[entry] = wellsdivided
#    return(edict)

#Future
class exptemplate:
    def __init__(self, entry):
        self.name = entry
        self.reagents = 'null'
        self.chemicals = 'null'