import logging
import itertools
import sys

import pandas as pd

from capture.generate import calcs
from capture.models import chemical
from capture.generate.wolframsampler import WolframSampler
from capture.generate.qrandom import get_unique_chemical_names, build_reagent_vectors
import capture.devconfig as config

modlog = logging.getLogger('capture.generate.statespace')


##generate a state set from the volume constraints of the experimental system ensuring that the limits are met, return the full df of volumes as well as the idealized conc df
def default_statedataframe(rxndict, expoverview, vollimits, rdict, experiment, volspacing):
    portionnum = 0
    prdf = pd.DataFrame()
    prmmoldf = pd.DataFrame()
    fullreagentnamelist=[]
    fullvollist=[]
    for portion in expoverview:
        reagentnamelist=[]
        reagentvols=[]
        # generate the list of possible volumes for each reagent and the associated mmol calculated values (for parsing later)
        for reagent in portion:
            reagentvols.append((list(range(0, vollimits[portionnum][1]+1, volspacing)))) #Take the maximum volume limit and generate a list of all possible volumes from 0 to the max
            reagentnamelist.append('Reagent%s (ul)'%reagent)
            fullreagentnamelist.append('Reagent%s (ul)'%reagent)
        #generate permutation of all of the volumes
        testdf = pd.DataFrame((list(itertools.product(*reagentvols))))
        testdf.astype(int)
        #organize dataframe with the sums of the generated numbers
        sumdf=(testdf.sum(axis=1))
        sumname='portion%s_volsum'%portionnum
        reagentnamelist.append(sumname)
        rdf = pd.concat([testdf, sumdf], axis=1, ignore_index=True)
        rdf.columns = reagentnamelist
        # Select only those which meet the volume critera specified by the portion of the experiment
        finalrdf = ((rdf.loc[(rdf[sumname] >= int(vollimits[portionnum][0])) & (rdf[sumname] <= int(vollimits[portionnum][1]))]))
        finalrdf = finalrdf.drop(labels=sumname, axis=1)
        fullvollist.append(finalrdf.values.tolist())
        portionnum+=1
    #permute all combinations of the portions that meeet the requirements set by the user
    fullpermlist = (((list(itertools.product(*fullvollist)))))
    # combine the list of list for each rxn into a single list for import into pandas
    finalfulllist=[]
    for multivol in fullpermlist:
        finalfulllist.append(list(itertools.chain.from_iterable(multivol)))
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
        else:
            pass
    return(prdf,finalmmoldf)

def wolfram_statedataframe(rxndict, expoverview, vollimits, rdict, experiment, volspacing):
    ws = WolframSampler()
    portionnum = 0
    prdf = pd.DataFrame()
    prmmoldf = pd.DataFrame()
    fullreagentnamelist=[]
    fullvollist=[]
    for portion in expoverview:

        maxconc = rxndict.get('max_conc', 15)
        portion_reagents = [rdict[str(i)] for i in portion]
        volmax = vollimits[portionnum][1]
        portion_species_names = get_unique_chemical_names(portion_reagents)
        reagent_vectors = build_reagent_vectors(portion_reagents, portion_species_names)
        experiments = ws.enumerativelySample(reagent_vectors,  float(maxconc), float(config.volspacing), float(volmax))

        experiment_df = pd.DataFrame.from_dict(experiments)
        # todo: aaron accumulate experiments in a df somewhere
        # todo we can also scrap portions entirely when wolfram is on? (since we will have the trivial number of poritons (1)
        # todo but its best to leave them in for now until we talk to ian



    finalmmoldf = pd.DataFrame()
    # todo: aaron something might have to happen with the names here
    for reagentname in fullreagentnamelist:
        if "Reagent" in reagentname:
            reagentnum = reagentname.split('t')[1].split(' ')[0]
            mmoldf = calcs.mmolextension(prdf[reagentname], rdict, experiment, reagentnum)
            finalmmoldf = pd.concat([finalmmoldf,mmoldf], axis=1)
        else:
            pass
    ws.terminate()
    return prdf, finalmmoldf

def chemicallist(rxndict):
    chemicallist = []
    for k,v in rxndict.items():
        if 'abbreviation' in k:
            name = k.split('m')[1].split('_')[0]
            chemicallist.append(name)
    return(chemicallist)

def statepreprocess(chemdf, rxndict, edict, rdict, volspacing):
    experiment = 1
    modlog.info('Making a total of %s unique experiments on the tray' %rxndict['totalexperiments'])
    erdf = pd.DataFrame() 
    ermmoldf = pd.DataFrame()
    while experiment < rxndict['totalexperiments']+1:
        modlog.info('Initializing dataframe construction for experiment %s' %experiment)
        experimentname = 'exp%s' %experiment
        for k,v in edict.items():
            if experimentname in k:
                if 'wells' in k:
                    wellnum = int(v)
                if 'vols' in k:
                    vollimits=(v)
                else:
                    pass
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
    emsumdf = emsumdf.divide(erdf.sum(axis=1), axis='rows')*1000
#    plotter.plotme(ReagentmmList[0],ReagentmmList[1], hold.tolist())
    #combine the experiments for the tray into one full set of volumes for all the wells on the plate
    modlog.info('Begin combining the experimental volume dataframes')
#    for chemical in rdict['2'].chemicals:
#        print(rxndict['chem%s_abbreviation' %chemical])
    return(erdf,ermmoldf,emsumdf)