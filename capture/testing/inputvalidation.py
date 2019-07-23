import sys
import logging
import re
from utils.data_handling import get_explicit_experiments, flatten
import capture.devconfig as config
from utils import globals

modlog = logging.getLogger(__name__)

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
    """Makes sure well counts from all experiments (random and manual) sum to run-level wellcount
    """

    modlog = logging.getLogger('capture.prebuildvalidation.expcount')
    expwells = []
    expcount = 0

    exp_id_pat = re.compile('^exp\d+$')
    exp_well_pat = re.compile('^exp\d+_wells$')  # TODO is this too restrictive?

    for k, v in rxndict.items():
        if exp_id_pat.search(k.strip()):
            expcount += 1
        if exp_well_pat.search(k.strip()):
            expwells.append(v)

    manual_wells = rxndict.get('manual_wells', 0)

    if sum(expwells) + manual_wells > rxndict['wellcount']:
        modlog.error("Experiments requested outnumber allotted wells. Check well counts for each experiment")
        sys.exit()

    elif sum(expwells) + manual_wells < rxndict['wellcount']:
        modlog.error("Experiments requested do not sum to the allotted wells. Check well counts for each experiment")
        sys.exit()

    modlog.info("Only 1 experiment specified. Wellcount applies to only experiment")


def used_reagents_are_specified(rxndict, template, reagent_alias):
    """Ensure that if a reagent is used in an experiment, it is specified"""
    

    # get the set of reagents specified in the template
    REAGENT_SPEC_PAT = re.compile('Reagent(\d+)_(chemical_list|ID)')
    SPECIFIED_REAGENTS = set(
        [int(REAGENT_SPEC_PAT.search(k).group(1))
         for k in rxndict.keys()
         if REAGENT_SPEC_PAT.search(k)]
    )

    def validate_random_reagents(rxndict):
        """Find the set of reagents that are used in randomly generated experiments but not specified"""

        used_reagents = []
        for k in rxndict.keys():
            if re.search('^exp\d+$', k.strip()):
                used_reagents.extend(rxndict[k])
        used_reagents = set(flatten(used_reagents))

        used_unspecified = sorted(list(used_reagents - SPECIFIED_REAGENTS))

        return used_unspecified

    def validate_manual_reagents(template):
        """Find the set of reagents that are used in manually entered experiments but not specified"""

        reagent_pat = re.compile('Reagent(\d+) \(ul\)')
        manual_experiments = get_explicit_experiments(template)

        used_reagents = manual_experiments.columns[manual_experiments.sum().values > 0]
        used_reagents = set(
                        [int(reagent_pat.search(reagent).group(1))
                         for reagent in used_reagents
                         if reagent_pat.search(reagent)]
                        )
        used_unspecified = sorted(list(used_reagents - SPECIFIED_REAGENTS))

        return used_unspecified

    if config.sampler != 'wolfram':
        # TODO: discuss at code review: is it time for a better fix of this wolfram problem?
        unspecified_random = validate_random_reagents(rxndict)
        if unspecified_random:
            raise ValueError(f'{reagent_alias}(s) {unspecified_random} were used in random experiment specification '
                             f'but not specified')

    unspecified_manual = validate_manual_reagents(template)
    if unspecified_manual:
        raise ValueError(f'{reagent_alias}(s) {unspecified_manual} were used in manual experiment specification '
                         f'but not specified')

    return

def userinterface(rxndict):
    assert isinstance(rxndict['exp1'], list), 'exp1 in user XLS must be specified as a list of lists'


def reagconcdefs(rxndict):
    for k,v in rxndict.items():
        pass


def validate_solvent_positions(rdict, solventlist, reagent_alias, chemdf):
    """Check that the last chemical in the reagent is a solvent, and that all other chemicals are not solvents"""

    # loop over reagents in order to keep things a little prettier for the user in case of multiple failures
    for reagent_index in sorted(rdict.keys()):
        reagent = rdict[reagent_index]

        reagent_solvents = [chemical for chemical in reagent.chemicals if chemical in solventlist]
        num_solvents = len(reagent_solvents)

        if num_solvents > 1:
            modlog.warning(f'You are using {num_solvents} in {reagent_alias}{reagent_index}, '
                           f'be aware of nonideal mixing')

        if num_solvents >= 1 and reagent.chemicals[-1] not in solventlist :
            raise ValueError(f'Solvents should appear last. {reagent_solvents[-1]} is a solvent ' 
                             f'but does not appear last in {reagent_alias}{reagent_index}')

        if num_solvents == 0:

            densities = chemdf.filter(regex='[Dd]ensity')

            if densities.shape[1] > 1:
                raise ValueError('Multiple density columns detected in Chemical Inventory')

            last_chemical = reagent.chemicals[-1]
            density = densities.loc[last_chemical]

            try:
                float(density)
            except ValueError:
                # density is unspecified. We'll raise our own error here
                raise ValueError(f'No solvents specified in {reagent_alias}{reagent_index} '
                                 f'and {last_chemical} has no density in Chemical Inventory')
            else:
                # density was specified
                modlog.warning(f'No solvents specified in {reagent_alias}{reagent_index} ')

    return

def postbuildvalidation(rxndict, vardict, rdict, edict, chemdf):
    reagent_alias = config.lab_vars[globals.get_lab()]['reagent_alias']

    modlog = logging.getLogger('capture.postbuildvalidation')
#        modlog.error("Fatal error. Reagents and chemicals are over constrained. Recheck user options!")
    validate_solvent_positions(rdict, vardict['solventlist'], reagent_alias, chemdf)
    modlog.info('Experiment successfully constructed.')

def prebuildvalidation(rxndict, vardict):
    '''handles validation functions for xls input file

    takes the rxndict as input and performs validation on the input to ensure the proper structure
    -- currently underdeveloped
    '''
    reagent_alias = config.lab_vars[globals.get_lab()]['reagent_alias']
    modlog = logging.getLogger('capture.prebuildvalidation')
    userinterface(rxndict)
    expcount(rxndict)
    expwellcount(rxndict)
    reagconcdefs(rxndict)
    used_reagents_are_specified(rxndict, vardict['exefilename'], reagent_alias)
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