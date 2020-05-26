import logging
import optunity
import pandas as pd
import numpy as np
import random
import sys

from capture.generate.wolframsampler import WolframSampler
from capture.testing import inputvalidation
from capture.models import chemical
from capture.generate import calcs
import capture.devconfig as config
from utils.data_handling import get_explicit_experiments, get_reagent_number_as_string
from utils import globals

modlog = logging.getLogger('capture.generate.qrandom')


def rdfbuilder(rvolmaxdf, rvolmindf, reagent, wellnum):
    count = 0 
    reagentname = "Reagent%s (ul)" %reagent
    reagentlist = []
    while count < wellnum:
        volmax = rvolmaxdf[count]
        volmin = rvolmindf[count]
        reagentitem = random.randint(volmin,volmax)
        reagentlist.append(reagentitem)
        count+=1
    rdf = pd.DataFrame({reagentname:reagentlist}).astype(int)
    return(rdf)

def f(x1):
    return 0.0

def initialrdf(volmax, volmin, reagent, wellnum):
    _, info_random, _ = optunity.minimize(f, num_evals=wellnum, x1=[volmin, volmax], solver_name='random search')
    ##Create quasi-random data spread
    reagentlist=info_random.call_log['args']['x1'] #Create reagent amounts (mmol), change x variable to change range, each generated from unique sobol index
    reagentname = "Reagent%s (ul)" %reagent
    rdf = pd.DataFrame({reagentname:reagentlist}).astype(int)
    return(rdf)
    #Generate a range of Amine concentrations dependent upon the range possible due to the presence of amine in Stock solution A \

#very similar to vollimtcont
def calcvollimit(userlimits, rdict, volmax, volmin, experiment, reagentlist, reagent, wellnum): 
    rdata = rdict['%s'%reagent]
#    chemicals = rdata.chemicals
    possiblemaxvolumes = []
    possiblemaxvolumes.append(volmax)
    possibleminvolumes = []
    possibleminvolumes.append(volmin)
    # Take the values determined from the user constraints and pass along the relevant value to the calling function
    if (min(possiblemaxvolumes)) != volmax:
        # Flag that there are constraints so that the user is aware they are limiting the total physical space artificially
        modlog.warning("User has constrained the maximum search space by lowering the maximum value for a chemical in experiment %s reagent %s, be sure this is intentional" % (experiment, reagent))
        volmax = min(possiblemaxvolumes)
    if (max(possibleminvolumes)) != volmin:
        modlog.warning("User has constrained the maximum search space by raising the minimum value for a chemical in experiment %s reagent %s, be sure this is intentional" % (experiment, reagent))
        volmin = max(possibleminvolumes)
    else: pass
    # Testing functions to ensure that all requirements / conditions for the volume are being met appropriately regardless of user specification
#    testing.reagenttesting(volmax,volmin)
    return(volmax, volmin)

def totalmmolchemicals(chemicals, usedchems, mmoldf):
    finalsummedmmols = pd.DataFrame()
    for chemical in chemicals:
        headerlist = []
        cfullname = 'chemical%s' %chemical
        for header in usedchems:
            if cfullname in header:
                headerlist.append(header)
        tempdf = pd.DataFrame()
        for header in headerlist:
            tempdf = pd.concat([tempdf, mmoldf[header]], axis=1)
        summedmmols = pd.DataFrame(tempdf.sum(axis=1))
        summedmmols.columns = ['mmol_%s' %cfullname]
        finalsummedmmols = pd.concat([finalsummedmmols, summedmmols], axis=1)
    finalsummedmmols.fillna(value=0, inplace=True) # Total mmmols added of each chemical in previous reagent additions
    return(finalsummedmmols)

def calcvollimitdf(rdf, mmoldf, userlimits, rdict, volmax, volmin, experiment, reagentlist, reagent, wellnum, rxndict): 
    # Create dataframes which will hold the final comparisons for the max and min
    finalvolmaxdf = pd.DataFrame()
    # Get the maximum volumes possible for this particular reagent based on user constraints
    rvolmax, rvolmin = calcvollimit(userlimits,
                                    rdict,
                                    volmax,
                                    volmin,
                                    experiment,
                                    reagentlist,
                                    reagent,
                                    wellnum)
    # get maximum values based on experimental constraints (well volume primarily)
    inputvalidation.reagenttesting(volmax,volmin)
    # Generate an upward limit for the chemical in dataframe based on the maximum user specified well volume and all previously used reagents
    volmaxdf = volmax - rdf.sum(axis=1)
    finalvolmaxdf = pd.concat([finalvolmaxdf, volmaxdf], axis=1)
    #replace values of experimental constraints with values of the reagent constraints (tighter) if experiment is looser 
    volmaxdf[volmaxdf > rvolmax] = rvolmax
    finalvolmaxdf = pd.concat([finalvolmaxdf, volmaxdf], axis=1)
    #remove reagent volume to adjust for constraints set by user for final concentration limits
    rdata = rdict['%s'%reagent]
    chemicals = rdata.chemicals
    usedchemsobj = mmoldf.columns
    usedchems = []
    # Blank dataframe of minimums of appropriate length
    blanklist = [0]*wellnum
    finalvolmindf = pd.DataFrame(blanklist)
    # build a list of headers of chemicals used previously
    for chem in usedchemsobj:
        usedchems.append(chem)
    #pile chemicals (and how much) from past reaction into a single frame to ensure constraints are met
    finalsummedmmols = totalmmolchemicals(chemicals, usedchems, mmoldf)
    # This function is to ensure that a user set constraints in the execution script (molar max and min for achemical ) are met for each well
    # The first draw that we are matching against calculated this information for the first reagent, now we have ensure that the remaining volume doesn't push
    #   the experiment beyond the user set limits of the system.
    # Look at each chemical in the chemical list of the reagent
    for chemical in chemicals:
        try: #Potentially could be an if statement, but the search for the chem#_molarmax or chem#_molarmin will fail if no value is set a workaround could be to set hard coded far limits and flag errors
            header = 'mmol_%s' %chemical
            chemconc = rdata.concs['conc_chem%s' %chemical]
            # calculate the remaining mmols of the chemical  based on the user set limits
            volmaxdf = ((rxndict['chem%s_molarmax' %chemical]*rvolmax/1000)-finalsummedmmols[header]) / chemconc * 1000
            finalvolmaxdf = pd.concat([finalvolmaxdf, volmaxdf], axis=1)
        except Exception:
            pass
    # do it all again for the minimums, ensure that the user set minimums are met if this is the final reagent with a particular chemical
        try:
            header = 'mmol_%s' %chemical
            chemconc = rdata.concs['conc_chem%s' %chemical]
            volmindf = ((rxndict['chem%s_molarmin' %chemical]*rvolmax/1000)-finalsummedmmols[header]) / chemconc * 1000
            volmindf[volmindf < 0] = 0
            finalvolmindf = pd.concat([finalvolmindf, volmindf], axis=1)
        except Exception:
            pass
    # Take the minimum of the maximums for the volumes calculated throughout this process
    outvolmaxdf = finalvolmaxdf.min(axis=1)
    # Take the maximum minimum ... 
    outvolmindf =  finalvolmindf.max(axis=1) 
    # Return the relevant datasets as int values (robot can't dispense anything smaller so lose the unsignificant figures /s)
    return(outvolmaxdf.astype(int), outvolmindf.astype(int))


def default_sampling(expoverview, rdict, vollimits, rxndict, wellnum, userlimits, experiment, portion_start_idx=0):
    """Ian's original sampling implementation.

    Performs samplings within portions of the expoverview, starting from portion_start_idx

    :return: (experiment volume df, experiment mmol df, version number of this sampler)
    """
    version = 2.7 # random sampling >3 chemicals (non-zero), maintains random sampling on secondary portions
    prdf = pd.DataFrame()
    prmmoldf = pd.DataFrame()

    portionnum = portion_start_idx
    while portionnum < len(expoverview):
        # need the volume minimum and maximum and well count
        reagentcount = 1
        reagenttotal = len(expoverview[portionnum])

        # Determine from the chemicals and the remaining volume the maximum and
        # minimum volume possible for the sobol method

        volmax = vollimits[portionnum][1]

        # unoptimized code that ensure that the previous reagents are considered and that the final reagent accurately
        # fills to the minimum volume set by the users "fill to" requirement

        rdf = pd.DataFrame()
        mmoldf = pd.DataFrame()
        finalrdf = pd.DataFrame()
        finalmmoldf = pd.DataFrame()

        for reagent in expoverview[portionnum]:
            finalvolmin = vollimits[portionnum][0]
            if reagentcount == 1:
                if len(expoverview[portionnum]) == 1:
                    volmin = vollimits[portionnum][0]
                    volmax = vollimits[portionnum][1] + 0.00001
                else:
                    volmin = 0

                # since all of the volume limits for the first draw are the same these can be
                # treated as a bounded search sequence
                rvolmax, rvolmin = calcvollimit(userlimits,
                                                rdict,
                                                volmax,
                                                volmin,
                                                experiment,
                                                expoverview[portionnum],
                                                reagent,
                                                wellnum)

                # Returns datafram of volumes of each reagent added to each experiment
                rdf = initialrdf(rvolmax, rvolmin, reagent, wellnum)

                # Returns mmol specified dataframe for each experiment, reagent, and
                # chemical (<-- values are in the header) have been generated for this portion of the experiment

                mmoldf = calcs.mmolextension((rdf['Reagent%s (ul)' %reagent]), rdict, experiment, reagent)
                reagentcount += 1
            # operate within the available ranges taken from the previous constraints
            elif reagentcount < reagenttotal:
                # The constraints on the middle draws are more complicated and are dependent upon the first,
                # a different sampling strategy must be used
                # (i.e. this is not going to use sobol as the ranges are different for each)
                # Constrain the range based on volume, reagent-chemical concentrations and user constraints

                rvolmaxdf, rvolmindf = calcvollimitdf(finalrdf,
                                                      mmoldf,
                                                      userlimits,
                                                      rdict,
                                                      volmax,
                                                      volmin,
                                                      experiment,
                                                      expoverview[portionnum],
                                                      reagent,
                                                      wellnum,
                                                      rxndict)
                # Since each volume maximum is different, need to sample the remaining reagents independently
                # (thus different sampling)
                rdf = rdfbuilder(rvolmaxdf, rvolmindf, reagent, wellnum)
                mmoldf = calcs.mmolextension((rdf['Reagent%s (ul)' %reagent]), rdict, experiment, reagent)
                reagentcount += 1

            # Ensure that the final round meets the lower bounds and upper bound total
            # fill volume requirements of the user
            elif reagentcount == reagenttotal:
                if vollimits[portionnum][0] == vollimits[portionnum][1]:
                    # print(finalrdf.sum(axis=1))
                    rvolmaxdf, rvolmindf = calcvollimitdf(finalrdf,
                                                          mmoldf,
                                                          userlimits,
                                                          rdict,
                                                          volmax,
                                                          volmin,
                                                          experiment,
                                                          expoverview[portionnum],
                                                          reagent,
                                                          wellnum,
                                                          rxndict)
                    reagentname = "Reagent%s (ul)" % reagent
                    rdf = pd.DataFrame(rvolmaxdf, columns=[reagentname])
                    mmoldf = calcs.mmolextension((rdf['Reagent%s (ul)' % reagent]), rdict, experiment, reagent)
                else:
                    rvolmaxdf, rvolmindf = calcvollimitdf(finalrdf, mmoldf, userlimits, rdict, volmax, volmin,
                                                          experiment, expoverview[portionnum], reagent, wellnum, rxndict)
                    rvolmindf = ensuremin(rvolmindf, finalrdf, finalvolmin)
                    rdf = rdfbuilder(rvolmaxdf, rvolmindf, reagent, wellnum)
                    mmoldf = calcs.mmolextension(rdf['Reagent%s (ul)' % reagent], rdict, experiment, reagent)
                reagentcount += 1
            else:
                modlog.error("Fatal error.  Unable to effectively parse reagent%s in portion %s.  \
                Please make sure that the selected values make chemical sense!" % (reagent, expoverview[portionnum]))
            finalrdf = pd.concat([finalrdf, rdf], axis=1)
            finalmmoldf = pd.concat([finalmmoldf, mmoldf], axis=1)

        prdf = pd.concat([prdf, finalrdf], axis=1)
        prmmoldf = pd.concat([prmmoldf, finalmmoldf], axis=1)
        portionnum += 1

    return prdf, prmmoldf, version

def ensuremin(rvolmindf, finalrdf, finalvolmin):
    """Its a clamp! -- https://upload.wikimedia.org/wikipedia/en/6/6e/AckbarStanding.jpg
    """
    currvoldf = finalrdf.sum(axis=1)
    trumindf = finalvolmin - currvoldf
    rvolmindf[rvolmindf < trumindf] = trumindf
    return rvolmindf

def get_unique_chemical_names(reagents):
    """Get the unique chemical species names in a list of reagents.

    The concentrations of these species define the vector space in which we sample possible experiments

    :param reagents: a list of perovskitereagent objects
    :return: a list of the unique chemical names in all of the reagent
    """
    chemical_species = set()

    if isinstance(reagents, dict):
        reagents = [v for v in reagents.values()]

    for reagent in reagents:
        chemical_species.update(reagent.chemicals)
    return sorted(list(chemical_species))


def build_reagent_vectors(portion_reagents, portion_chemicals):
    """Write the reagents in a vector form, where the vectors live in the complete portion basis

    The basis is spanned by all chemicals in all reagents in the portion (sans solvent)

    :param portion_reagents: a list of all reagents in the portion
    :param portion_chemicals: a list of all chemical names in the poriton
    :param rdict:
    :return:
    """

    # find the vector representation of the reagents in concentration space
    reagent_vectors = {}
    if isinstance(portion_reagents, dict):
        portion_reagents = [v for v in portion_reagents.values()]

    for reagent in portion_reagents:
        name = 'Reagent{} (ul)'.format(reagent.name)
        comp_dict = reagent.component_dict
        vec = [comp_dict.get(elem, 0) for elem in portion_chemicals]
        reagent_vectors[name] = vec

    return reagent_vectors

def volume_to_mmol_wrapper(vol_df, rdict, experiment):
    portion_mmol_df = pd.DataFrame()
    for columnname in vol_df.columns:
        reagent = int(get_reagent_number_as_string(columnname))  # 'Reagent2 (ul)' to give '2'
        mmol_df = calcs.mmolextension((vol_df[columnname]), rdict, experiment, reagent)
        portion_mmol_df = pd.concat([portion_mmol_df, mmol_df], axis=1)

    return portion_mmol_df

def wolfram_sampling(expoverview, rdict, old_reagents, vollimits, rxndict, vardict, wellnum, userlimits, experiment):
    """Sample from the convex hull defined in species concentration space with uniform probability

    Any portions defined in the experiment overview beyond the first will be sampled by the default_sampler

    :param old_reagents:
    :param vardict:

    :return: (experiment volume df, experiment mmol df, version number of this sampler)
    """
    experiment_mmol_df = pd.DataFrame()
    experiment_df = pd.DataFrame()

    version = 1.2 # original "expert sampling"

    if len(expoverview) > 1:
        modlog.warning('only first portion will use mathematica sampler')
    portionnum = 0
    portion = expoverview[portionnum]

    volmax = vollimits[portionnum][1]
    maxconc = rxndict.get('max_conc', 15)

    portion_reagents = [rdict[str(i)] for i in portion]
    portion_species_names = get_unique_chemical_names(portion_reagents)
    reagent_vectors = build_reagent_vectors(portion_reagents, portion_species_names)

    if rxndict.get('multi_stock_sampling'):
        old_reagent_species_names = get_unique_chemical_names(old_reagents)
        ## todo: move to validation
        #if old_reagent_species_names != portion_species_names:
        #    modlog.error(("Old and new reagents must be made out of the same chemicals." +
        #                  f"\nNew reagent chemicals: {portion_species_names}" +
        #                  f"\nOld reagent chemicals: {old_reagent_species_names}"))
        #    sys.exit(1)
        old_reagent_vectors = build_reagent_vectors(old_reagents, old_reagent_species_names)
    else:
        old_reagent_vectors = None

    ws = WolframSampler()
    experiments = ws.randomlySample(reagent_vectors,
                                    old_reagent_vectors,
                                    int(wellnum),
                                    float(maxconc),
                                    float(volmax))
    ws.terminate()
    #TODO: the randomly sample returns bogus entires (doesn't error) if the run is not properly constructure
    # Validation should be done prior to feeding into mathematica
    try:
        portion_df = pd.DataFrame.from_dict(experiments)
    except ValueError:
        modlog.error(f'The .xlsx specification cannot be used to generate samples!') 
        modlog.error(f'Please ensure the run is correctly specified. See FAQs for suggestions.')
        print(f'User information and FAQs can be found at: https://docs.google.com/document/d/1RQJvAlDVIfu19Tea23dLUSymLabGfwJtDnZwANtU05s/edit#bookmark=id.8sg0qwagd7yw')
        import sys
        sys.exit()
    # todo How long can this reagent 6/7 hotfix remain like this?
    if rxndict['ExpWorkflowVer'] <= 1.1:
        if rxndict['lab'] == 'LBL':
            portion_df['Reagent6 (ul)'] = np.floor(portion_df['Reagent7 (ul)'] / 2).astype(int)
            portion_df['Reagent7 (ul)'] = np.ceil(portion_df['Reagent7 (ul)'] / 2).astype(int)
            rdict['6'] = rdict['7']


    portion_mmol_df = pd.DataFrame()
    for col in portion_df.columns:
        reagent = int(col.split('t')[1].split('(')[0])  # 'Reagent2 (ul)' to give '2'
        mmol_df = calcs.mmolextension((portion_df[col]), rdict, experiment, reagent)
        portion_mmol_df = pd.concat([portion_mmol_df, mmol_df], axis=1)

    experiment_mmol_df = pd.concat([experiment_mmol_df, portion_mmol_df], axis=1)
    experiment_df = pd.concat([experiment_df, portion_df], axis=1)

    portionnum +=1
    if portionnum < len(expoverview):
        modlog.warn("Using default sampler for portion 2, mathematica sampling not supported for greater than first portion")
        # version2 variable doesn't get used in this case, toss to a garbage variable and retain the mathematica version
        prdf, prmmoldf, version2 = default_sampling(expoverview,
                                           rdict,
                                           vollimits,
                                           rxndict,
                                           wellnum,
                                           userlimits,
                                           experiment,
                                           portion_start_idx=portionnum)
        experiment_mmol_df = pd.concat([experiment_mmol_df, prmmoldf], axis=1)
        experiment_df = pd.concat([experiment_df, prdf], axis=1)

    return experiment_df, experiment_mmol_df, version

def preprocess_and_sample(chemdf, vardict, rxndict, edict, rdict, old_reagents, climits):

    """generates a set of random reactions within given reagent and user constraints

    requires the chemical dataframe, rxndict (with user inputs), experiment dictionary, 
    reagent dictionary and chemical limits (climits) -- update should enable easier
    inspection of these elements
    """
    experiment = 1
    modlog.info('Making a total of %s unique experiments on the tray' % rxndict['totalexperiments'])
    erdf = pd.DataFrame() 
    ermmoldf = pd.DataFrame()
    exportable_model_df = pd.DataFrame()

    # outer loop over experiments in Template
    while experiment < rxndict['totalexperiments']+1:
        modlog.info('Initializing dataframe construction for experiment %s' %experiment)
        experimentname = 'exp%s' % experiment

        # gross loop to get wellnum and vollimits
        # todo: factor out this loop
        for k, v in edict.items():
            if experimentname in k:
                if 'wells' in k:
                    num_wells = int(v)
                if 'vols' in k:
                    vollimits = v

        if num_wells == 0:
            experiment += 1
            continue

        modlog.info('Building reagent constraints for experiment %s using reagents %s for a total of %s wells'
                    % (experiment, edict[experimentname], num_wells))

        # DO THE SAMPLING
        if config.sampler == 'wolfram':
            prdf, prmmoldf, version = wolfram_sampling(edict[experimentname],
                                              rdict,
                                              old_reagents,
                                              vollimits,
                                              rxndict,
                                              vardict,
                                              num_wells,
                                              climits,
                                              experiment)
            if rxndict.get('multi_stock_sampling'):
                sampler_name = 'MathematicaMultiStock'
            else:
                sampler_name = 'MathematicaUniformRandom'
            globals.set_sampler(sampler_name, version)
        elif config.sampler == 'default':
            
            prdf, prmmoldf, version = default_sampling(edict[experimentname],
                                              rdict,
                                              vollimits,
                                              rxndict,
                                              num_wells,
                                              climits,
                                              experiment)
            sampler_name = 'ExpertQuasiRandom'
            globals.set_sampler(sampler_name, version)
        else:
            modlog.error('Encountered unexpected sampler in devconfig: {}. Exiting.'.format(config.sampler))
            sys.exit(1)

        erdf = pd.concat([erdf, prdf], axis=0, ignore_index=True, sort=True)
        ermmoldf = pd.concat([ermmoldf, prmmoldf], axis=0, ignore_index=True, sort=True)

        model_info_dict = {'modelname': [globals.get_sampler_uid()],'participantname':['escalate']}
        model_info_df =  pd.DataFrame.from_dict(model_info_dict)
        exportable_model_df = pd.concat([model_info_df]*erdf.shape[0], ignore_index=True)

        # Return the reagent data frame with the volumes for that particular portion of the plate
        modlog.info('Succesfully built experiment %s which returned.... ' %(experiment))
        experiment += 1

    if not rxndict['manual_wells'] == 0:

        manual_model_info_dict = {'modelname': [globals.get_manualruns_uid()],'participantname':[globals.get_manualruns_author()]}
        manual_model_info_df =  pd.DataFrame.from_dict(manual_model_info_dict)
        manual_exportable_model_df = pd.concat([manual_model_info_df]*int(rxndict['manual_wells']), ignore_index=True)
        
        specifiedExperiments = get_explicit_experiments(vardict['exefilename'])
        erdf = pd.concat([erdf, specifiedExperiments], axis=0, ignore_index=True, sort=True)
        specified_mmol_df = volume_to_mmol_wrapper(specifiedExperiments, rdict, 'f')
        ermmoldf = pd.concat([ermmoldf, specified_mmol_df], axis=0, ignore_index=True, sort=True)
        exportable_model_df = pd.concat([exportable_model_df, manual_exportable_model_df], axis=0, ignore_index=True, sort=True)


    # Final reagent volumes dataframe
    erdf.fillna(value=0, inplace=True)
    if not erdf.shape[0] == rxndict['wellcount']:
        raise ValueError("Too few reactions specified: \n" +\
                         "Ensure that all exp<index>_wells and manual_well sum to wellcount")
        
    # Final reagent mmol dataframe broken down by experiment, protion, reagent, and chemical
    ermmoldf.fillna(value=0, inplace=True)
    clist = chemical.exp_chem_list(rdict)

    # Final nominal molarity for each reagent in each well
    emsumdf = calcs.finalmmolsums(clist, ermmoldf) # Returns incorrectly labeled columns, we used these immediately and convert to the correct units
    emsumdf = emsumdf.divide(erdf.sum(axis=1), axis='rows')*1000

    # plotter.plotme(ReagentmmList[0],ReagentmmList[1], hold.tolist())
    # combine the experiments for the tray into one full set of volumes for all the wells on the plate
    modlog.info('Begin combining the experimental volume dataframes')
    
    # for chemical in rdict['2'].chemicals:
    #    print(rxndict['chem%s_abbreviation' %chemical])
    return erdf, ermmoldf, emsumdf, exportable_model_df
