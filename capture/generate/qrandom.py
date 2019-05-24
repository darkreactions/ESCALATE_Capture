import logging
import optunity
import pandas as pd
import random
import sys

from capture.testing import inputvalidation
from capture.models import chemical
from capture.generate import calcs

from wolframclient.language import wlexpr
from wolframclient.evaluation import WolframLanguageSession

modlog = logging.getLogger('capture.generate.qrandom')


class WolframSampler:

    def __init__(self):
        """A wrapper to generateExperiments.wls

        Written as a class so the Wolfram session is only once at __init__ time.
        """
        self.session = WolframLanguageSession()
        self.session.evaluate('<<./capture/generate/generateExperiments.wls')
        self._generateExperiments = self.session.function('generateExperiments')
        print(self.session.evaluate(wlexpr('Names["Global`*"]')))

    def generateExperiments(self, reagentVectors, nExpt=96, maxMolarity=9., finalVolume=500.):
        """Randomly sample possible experiments in the convex hull of concentration space defined by the reagentVectors

        Shadows default arguments set at Wolfram level.
        Currently does not expose processVaules argument.

        :param reagentVectors: a dictionary of vector representations of reagents living in species-concentration space
        :param nExpt: the number of samples to draw
        :param maxMolarity: the maximum concentration of any species: defines a hypercube bounding the convex hull
        :param finalVolume: a scalar to act on the concentrations to convert to desired volume
        :return: a dictionary mapping: {reagents => list(volumes)} where list(volumes) has length nExpt
        :raises TypeError: since Mathematica will fail silently on incorrect types
        """
        if not isinstance(reagentVectors, dict):
            raise TypeError('reagentVectors must be dict, got {}'.format(type(reagentVectors)))
        if not isinstance(nExpt, int):
            raise TypeError('nExpt must be int, got {}'.format(type(nExpt)))
        if not isinstance(maxMolarity, float):
            raise TypeError('maxMolarity must be float, got {}'.format(type(maxMolarity)))
        if not isinstance(finalVolume, float):
            raise TypeError('finalVolume must be float, got {}'.format(type(finalVolume)))

        return self._generateExperiments(reagentVectors, nExpt, maxMolarity, finalVolume)


def rdfbuilder(rvolmaxdf, rvolmindf, reagent, wellnum):
    count = 0 
    reagentname = "Reagent%s (ul)" %reagent
    reagentlist = []
    while count < wellnum:
        volmax = rvolmaxdf[count]
        volmin = rvolmindf[count]
#        _, info_random, _ = optunity.minimize(f, num_evals=1, x1=[volmin, volmax], solver_name='random search')
#        reagentitem=info_random.call_log['args']['x1'] #Create reagent amounts (mmol), change x variable to change range, each generated from unique sobol index
        reagentitem = random.randint(volmin,volmax)
        reagentlist.append(reagentitem)
        count+=1
    rdf = pd.DataFrame({reagentname:reagentlist}).astype(int)
    return(rdf)

## Determine the maximum concentration for a particular chemical in a reagent
#def maxconcdet(rdata, rnum, currchemical):
#    maxconc = 0
#    for chemid,conc in rdata['%s' %rnum].concs.items():
#        itemnum = chemid.split('m')[1]
#        chemical_list_name = rdata['%s'%rnum].chemicals[itemnum]
#        if currchemical in chemical_list_name:
#            if conc > maxconc:
#                maxconc = conc
#    return(maxconc)
#
## Determine the absolute maximum concentration for a particular chemical across all reagents in a portion of the experiment
#def absmaxcondet(rdata, rnum, currchemical, reagentlist):
#    maxconc = 0 
#    for reagent in reagentlist:
#        conc = (maxconcdet(rdata, reagent, currchemical))
#        if conc > maxconc:
#            maxconc =  conc
#    return(maxconc)

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
    # Determine if any user constraints override the maximum concentrations dependent on the volume limits
#    for chemical in chemicals:
#        #The code will update the maximum volume to meet the upper bound set by the user
#        try: 
#            maxconc = maxconcdet(rdict, reagent, chemical)
#            absmaxconc = absmaxcondet(rdict, reagent, chemical, reagentlist)
#            userdefinedmax = (userlimits['chem%s_molarmax'%chemical])
#            # Update the constraints / limits on the total volume of this reagent to fit within the restrictions that the user might have set
#            if userdefinedmax <= maxconc:
#                volmaxnew = userdefinedmax / maxconc * volmax
#                possiblemaxvolumes.append(int(volmaxnew))
#            # If other reagents in the portion of the reaction can access higher concentrations, don't error out
#            elif userdefinedmax <= absmaxconc:
#               pass
#            else: 
#                #In the case where this upperbound cannot be met the user has overconstrained the system
#                modlog.error("User defined concentration greater than physically possible for chemical%s in experiment %s" %(chemical, experiment))
#                sys.exit()
#        except Exception:
#            pass
#        #The code will update the minimum volume to meet the lower bound set by the user
#        try: 
#            reagconc = (rdata.concs['conc_chem%s' %chemical])
#            userdefinedmin = (userlimits['chem%s_molarmin'%chemical])
#            absmaxconc = absmaxcondet(rdict, reagent, chemical, reagentlist)
#            if userdefinedmin >= 0:
#                if reagconc < absmaxconc: 
#                    pass
#                else:
#                    volminnew = userdefinedmin / reagconc * volmax
#                    possibleminvolumes.append(int(volminnew))
#            elif userdefinedmax <= absmaxconc:
#                pass
#            else: pass
#        except Exception:
#            pass
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
    rvolmax, rvolmin = calcvollimit(userlimits, rdict, volmax, volmin, experiment, reagentlist, reagent, wellnum)
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


def get_unique_chemical_names(reagents):
    """Get the unique chemical species names in a list of reagents.

    The concentrations of these species define the vector space in which we sample possible experiments

    :param reagents: a list of perovskitereagent objects
    :return: a list of the unique chemical names in all of the reagent
    """
    chemical_species = set()
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
    for reagent in portion_reagents:
        name = 'Reagent{} (ul)'.format(reagent.name)
        comp_dict = reagent.component_dict
        vec = [comp_dict.get(elem, 0) for elem in portion_chemicals]
        reagent_vectors[name] = vec

    return reagent_vectors

def portiondataframe(expoverview, rdict, vollimits, rxndict, wellnum, userlimits, experiment):
    portionnum = 0
    prdf = pd.DataFrame()
    prmmoldf = pd.DataFrame()
    ws = WolframSampler()
    for portion in expoverview:

        # Determine from the chemicals and the remaining volume the maximum and minimum volume possible for the sobol method
        volmax = vollimits[portionnum][1]
        # unoptimized code that ensure that the previous reagents are considered and that the final reagent accurately fills to the minimum volume set by the users "fill to" requirement


        portion_reagents = [rdict[str(i)] for i in portion]
        portion_species_names = get_unique_chemical_names(portion_reagents)
        reagent_vectors = build_reagent_vectors(portion_reagents, portion_species_names)
        experiments = ws._generateExperiments(reagent_vectors)

        from pprint import pprint
        print('Reagent vectors:')
        pprint(reagent_vectors)
        print('\n"Wolfram output:"')
        pprint(experiments)

        import sys
        ws.session.terminate()
        sys.exit()

        # experiment_df = pd.DataFrame(experiments)
        # print(experiment_df.head())
        # mmoldf = calcs.mmolextension((rdf['Reagent%s (ul)' % reagent]), rdict, experiment, reagent)
        # rvolmaxdf, rvolmindf = calcvollimitdf(finalrdf, mmoldf, userlimits, rdict, volmax, volmin, experiment, portion,
        # reagent, wellnum, rxndict)
        # rvolmindf = ensuremin(rvolmindf, finalrdf, finalvolmin)
        rdf = rdfbuilder(rvolmaxdf, rvolmindf, reagent, wellnum)
        reagentcount += 1
        prdf = pd.concat([prdf, finalrdf], axis=1)
        prmmoldf = pd.concat([prmmoldf, finalmmoldf], axis=1)
        portionnum+=1
    return(prdf, prmmoldf)

def ensuremin(rvolmindf, finalrdf, finalvolmin):
    currvoldf = finalrdf.sum(axis=1)
    trumindf = finalvolmin - currvoldf
    rvolmindf[rvolmindf < trumindf] = trumindf
    return(rvolmindf)

def preprocess(chemdf, rxndict, edict, rdict, climits):
    ''' generates a set of random reactions within given reagent and user constraints

    requires the chemical dataframe, rxndict (with user inputs), experiment dictionary, 
    reagent dictionary and chemical limits (climits) -- update should enable easier
    inspection of these elements
    '''
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
        modlog.info('Building reagent constraints for experiment %s using reagents %s for a total of %s wells' %(experiment, edict[experimentname], wellnum) )
        prdf,prmmoldf = portiondataframe(edict[experimentname], rdict, vollimits, rxndict, wellnum, climits, experiment)
        erdf = pd.concat([erdf, prdf], axis=0, ignore_index=True, sort=True)
        ermmoldf = pd.concat([ermmoldf, prmmoldf], axis=0, ignore_index=True, sort=True)
        # Return the reagent data frame with the volumes for that particular portion of the plate
        modlog.info('Succesfully built experiment %s which returned.... ' %(experiment))
        experiment+=1
    #Final reagent volumes dataframe
    erdf.fillna(value=0, inplace=True)
    #Final reagent mmol dataframe broken down by experiment, protion, reagent, and chemical
    ermmoldf.fillna(value=0, inplace=True)
    clist = chemical.exp_chem_list(rdict)
    # Final nominal molarity for each reagent in each well
    emsumdf = calcs.finalmmolsums(clist, ermmoldf) # Returns incorrectly labeled columns, we used these immediately and convert to the correct units
    emsumdf = emsumdf.divide(erdf.sum(axis=1), axis='rows')*1000
#    plotter.plotme(ReagentmmList[0],ReagentmmList[1], hold.tolist())
    #combine the experiments for the tray into one full set of volumes for all the wells on the plate
    modlog.info('Begin combining the experimental volume dataframes')
#    for chemical in rdict['2'].chemicals:
#        print(rxndict['chem%s_abbreviation' %chemical])
    return(erdf,ermmoldf,emsumdf)
