import logging
import itertools
import sys

import pandas as pd
import numpy as np

from capture.generate import calcs
from capture.models import chemical
from capture.generate.wolframsampler import WolframSampler
from capture.generate.qrandom import get_unique_chemical_names, build_reagent_vectors
import capture.devconfig as config

modlog = logging.getLogger('capture.generate.statespace')

def default_statedataframe(rxndict, expoverview, vollimits, rdict, experiment, volspacing):
    """generate a state set from the volume constraints of the experimental system ensuring that the limits are met,
    return the full df of volumes as well as the idealized conc df
    :param rxndict:
    :param expoverview:
    :param vollimits:
    :param rdict:
    :param experiment:
    :param volspacing:
    :return:
    """
    portionnum = 0

    # TODO these two vars actually dont get used, just overwritten
    prdf = pd.DataFrame()
    prmmoldf = pd.DataFrame()

    fullreagentnamelist = []
    fullvollist = []

    for portion in expoverview:
        reagentnamelist = []
        reagentvols = []


        for reagent in portion:
            # generate the list of possible volumes for each reagent
            # and the associated mmol calculated values (for parsing later)

            # Take the maximum volume limit and generate a list of all possible volumes from 0 to the max
            reagentnamelist.append('Reagent%s (ul)' % reagent)
            reagentvols.append((list(range(0, vollimits[portionnum][1]+1, volspacing))))
            fullreagentnamelist.append('Reagent%s (ul)' % reagent)

        # generate permutation of all of the volumes
        testdf = pd.DataFrame((list(itertools.product(*reagentvols))))
        testdf.astype(int)

        # organize dataframe with the sums of the generated numbers
        sumdf = testdf.sum(axis=1)
        sumname = 'portion%s_volsum' % portionnum
        reagentnamelist.append(sumname)
        rdf = pd.concat([testdf, sumdf], axis=1, ignore_index=True)
        rdf.columns = reagentnamelist

        # Select only those which meet the volume critera specified by the portion of the experiment
        finalrdf = ((rdf.loc[(rdf[sumname] >= int(vollimits[portionnum][0])) & (rdf[sumname] <= int(vollimits[portionnum][1]))]))
        finalrdf = finalrdf.drop(labels=sumname, axis=1)
        fullvollist.append(finalrdf.values.tolist())
        portionnum += 1

    # permute all combinations of the portions that meet the requirements set by the user
    fullpermlist = (((list(itertools.product(*fullvollist)))))
    # combine the list of list for each rxn into a single list for import into pandas
    finalfulllist = []

    for multivol in fullpermlist:
        finalfulllist.append(list(itertools.chain.from_iterable(multivol)))

    # TODO replace with listcomp? listcomps are optimized at the interpreter-level
    # finalfulllist = [list(itertools.chain.from_iterable(multivol)) for multivol in fullpermlist]

    prdf = pd.DataFrame(finalfulllist)
    prdf = prdf.drop_duplicates()
    prdf.columns = fullreagentnamelist
    prdf.astype(float)
    finalmmoldf = pd.DataFrame()

    for reagentname in fullreagentnamelist:
        if "Reagent" in reagentname:
            reagentnum = reagentname.split('t')[1].split(' ')[0]
            mmoldf = calcs.mmolextension(prdf[reagentname], rdict, experiment, reagentnum)
            finalmmoldf = pd.concat([finalmmoldf,mmoldf], axis=1)

    return prdf, finalmmoldf


def wolfram_statedataframe(rxndict, expoverview, vollimits, rdict, experiment, volspacing):
    ws = WolframSampler()

    if len(expoverview) > 1:
        raise ValueError('When using wolfram sampling, expoverview must have length 1, got {}'.format(len(expoverview)))
    else:
        # portions don't make sense when using wolfram sampling
        # as a holdover we assume we have one an only one poriton and we hard code it here
        portionnum = 0
        portion = expoverview[portionnum]

    maxconc = rxndict.get('max_conc', 15)
    portion_reagents = [rdict[str(i)] for i in portion]
    volmax = vollimits[portionnum][1]
    portion_species_names = get_unique_chemical_names(portion_reagents)
    reagent_vectors = build_reagent_vectors(portion_reagents, portion_species_names)

    experiments = ws.enumerativelySample(reagentVectors=reagent_vectors,
                                        uniqueChemNames=portion_species_names,
                                        deltaV=float(config.volspacing),
                                        maxMolarity=float(maxconc),
                                        finalVolume=float(volmax))


    # todo: validate these two dfs downstream
    voldf = pd.DataFrame.from_dict(experiments['volumes'])
    concdf = pd.DataFrame.from_dict(experiments['concentrations'])

    ws.terminate()
    return voldf, concdf


def chemicallist(rxndict):

    chemicallist = []
    for k, v in rxndict.items():
        if 'abbreviation' in k:
            name = k.split('m')[1].split('_')[0]
            chemicallist.append(name)
    return chemicallist

def statepreprocess(chemdf, rxndict, edict, rdict, volspacing):
    """

    :param chemdf:
    :param rxndict:
    :param edict:
    :param rdict:
    :param volspacing:
    :return:
    """
    experiment = 1
    modlog.info('Making a total of %s unique experiments on the tray' %rxndict['totalexperiments'])
    erdf = pd.DataFrame() 
    ermmoldf = pd.DataFrame()

    while experiment < rxndict['totalexperiments'] + 1:
        modlog.info('Initializing dataframe construction for experiment %s' %experiment)
        experimentname = 'exp%s' % experiment
        for k, v in edict.items():
            if experimentname in k:
                if 'wells' in k:
                    wellnum = int(v)
                if 'vols' in k:
                    vollimits = v

        modlog.info('Building reagent state space for experiment %s using reagents %s' %(experiment, edict[experimentname]))
        modlog.warning('Well count will be ignored for state space creation!  Please disable CP run if this incorrect')

        if config.sampler == 'default':
            prdf, prmmoldf = default_statedataframe(rxndict, edict[experimentname], vollimits, rdict, experiment, volspacing)
        elif config.sampler == 'wolfram':
            prdf, prmmoldf = wolfram_statedataframe(rxndict, edict[experimentname], vollimits, rdict, experiment, volspacing)
        else:
            modlog.error('Unexpected sampler in devconfig: {}. Quitting.'.format(config.sampler))
            sys.exit(1)

        erdf = pd.concat([erdf, prdf], axis=0, ignore_index=True, sort=True)
        ermmoldf = pd.concat([ermmoldf, prmmoldf], axis=0, ignore_index=True, sort=True)
        # Return the reagent data frame with the volumes for that particular portion of the plate
        modlog.info('Succesfully built experiment %s stateset' %(experiment))
        experiment+=1

    #Final reagent volumes dataframe
    erdf.fillna(value=0, inplace=True)
    #Final reagent mmol dataframe broken down by experiment, protion, reagent, and chemical
    ermmoldf.fillna(value=0, inplace=True)
    clist = chemical.exp_chem_list(rdict)
    # Final nominal molarity for each reagent in each well
    # Final nominal molarity for each reagent in each well
    emsumdf = calcs.finalmmolsums(clist, ermmoldf) # Returns incorrectly labeled columns, we used these immediately and convert to the correct units

    if config.sampler == 'default':
        emsumdf = emsumdf.divide(erdf.sum(axis=1), axis='rows')*1000
#    plotter.plotme(ReagentmmList[0],ReagentmmList[1], hold.tolist())
    #combine the experiments for the tray into one full set of volumes for all the wells on the plate
    modlog.info('Begin combining the experimental volume dataframes')
#    for chemical in rdict['2'].chemicals:
#        print(rxndict['chem%s_abbreviation' %chemical])

    return erdf, ermmoldf, emsumdf