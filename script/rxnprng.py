import optunity
import pandas as pd
import numpy as np
from script import plotter
import logging
import sys
import random
from script import testing
import matplotlib.pyplot as plt


modlog = logging.getLogger('initialize.rxnprng')
                    
##Place holder function.  This can be fit to change the distribution of points at a later time. For now
## the method returns only the sobol value unmodified.  The sampling in each input x1, x2, x3 should be evenly distributed
## and unaltered.  (Blank function)
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

#very similar to vollimtcont
def calcvollimit(userlimits, rdict, volmax, volmin, experiment, reagentlist, reagent, wellnum): 
    rdata = rdict['%s'%reagent]
    chemicals = rdata.chemicals
    possiblemaxvolumes = []
    possiblemaxvolumes.append(volmax)
    possibleminvolumes = []
    possibleminvolumes.append(volmin)
    # Determine if any user constraints override the maximum concentrations dependent on the volume limits
    for chemical in chemicals:
        #The code will update the maximum volume to meet the upper bound set by the user
        try: 
            maxconc = maxconcdet(rdict, reagent, chemical)
            absmaxconc = absmaxcondet(rdict, reagent, chemical, reagentlist)
            userdefinedmax = (userlimits['chem%s_molarmax'%chemical])
            # Update the constraints / limits on the total volume of this reagent to fit within the restrictions that the user might have set
            if userdefinedmax <= maxconc:
                volmaxnew = userdefinedmax / maxconc * volmax
                possiblemaxvolumes.append(int(volmaxnew))
            # If other reagents in the portion of the reaction can access higher concentrations, don't error out
            elif userdefinedmax <= absmaxconc:
               pass
            else: 
                #In the case where this upperbound cannot be met the user has overconstrained the system
                modlog.error("User defined concentration greater than physically possible for chemical%s in experiment %s" %(chemical, experiment))
                sys.exit()
        except Exception:
            pass
        #The code will update the minimum volume to meet the lower bound set by the user
        try: 
            reagconc = (rdata.concs['conc_chem%s' %chemical])
            userdefinedmin = (userlimits['chem%s_molarmin'%chemical])
            absmaxconc = absmaxcondet(rdict, reagent, chemical, reagentlist)
            if userdefinedmin >= 0:
                if reagconc < absmaxconc: 
                    pass
                else:
                    volminnew = userdefinedmin / reagconc * volmax
                    possibleminvolumes.append(int(volminnew))
            elif userdefinedmax <= absmaxconc:
                pass
            else: pass
        except Exception:
            pass
    # Take the values determined from the user constraints and pass along the relevant value to the calling function
    if (min(possiblemaxvolumes)) != volmax:
        # Flag that there are constraints so that the user is aware they are limiting the total physical space artificially
        modlog.warning("User has constrained the maximum search space by lowering the maximum value for a chemical in experiment %s reagent %s, be sure this is intentional" % (experiment, reagent))
        volmax = min(possiblemaxvolumes)
    if (max(possibleminvolumes)) != 0:
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
    

def calcvollimitdf(rdf, mmoldf, userlimits, rdict, volmax, volmin, experiment, reagentlist, reagent, wellnum): 
    # Create dataframes which will hold the final comparisons for the max and min
    finalvolmaxdf = pd.DataFrame()
    # Get the maximum volumes possible for this particular reagent based on user constraints
    rvolmax, rvolmin = calcvollimit(userlimits, rdict, volmax, volmin, experiment, reagentlist, reagent, wellnum)
    # get maximum values based on experimental constraints (well volume primarily)
    testing.reagenttesting(volmax,volmin)
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
    for chemical in chemicals:
        try:
            header = 'mmol_chemical%s' %chemical
            chemconc = rdata.concs['conc_chem%s' %chemical]
#            print(chemconc, rvolmax)
            volmaxdf = rvolmax-(finalsummedmmols[header] / chemconc * 1000)
            finalvolmaxdf = pd.concat([finalvolmaxdf, volmaxdf], axis=1)
        except Exception:
            pass
    # do it all again for the minimums
        try:
            header = 'mmol_chemical%s' %chemical
            chemconc = rdata.concs['conc_chem%s' %chemical]
            volmindf = rvolmin-(finalsummedmmols[header] / chemconc * 1000)
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


# Determine the absolute maximum concentration for a particular chemical across all reagents in a portion of the experiment
def absmaxcondet(rdata, rnum, currchemical, reagentlist):
    maxconc = 0 
    for reagent in reagentlist:
        conc = (maxconcdet(rdata, reagent, currchemical))
        if conc > maxconc:
            maxconc =  conc
    return(maxconc)

# Determine the maximum concentration for a particular chemical in a reagent
def maxconcdet(rdata, rnum, currchemical):
    maxconc = 0
    chemname = 'conc_chem%s' %currchemical
    for chemid,conc in rdata['%s' %rnum].concs.items():
        if chemname in chemid:
            if conc > maxconc:
                maxconc = conc
    return(maxconc)

def mmolextension(reagentdf, rdict, experiment, reagent):
    mmoldf = (pd.DataFrame(reagentdf))
    portionmmoldf = pd.DataFrame()
    for chemical, conc in (rdict['%s' %reagent].concs.items()):
        chemname = chemical.split('m')[1]
        newmmoldf = mmoldf * conc / 1000
        newmmoldf.rename(columns={'Reagent%s (ul)'%reagent:'mmol_experiment%s_reagent%s_chemical%s' %(experiment, reagent, chemname)}, inplace=True)
        portionmmoldf = pd.concat([portionmmoldf, newmmoldf], axis=1)
    return(portionmmoldf)

def ensuremin(rvolmindf, finalrdf, finalvolmin):
    currvoldf = finalrdf.sum(axis=1)
    trumindf = finalvolmin - currvoldf
    rvolmindf[rvolmindf < trumindf] = trumindf
    return(rvolmindf)



def portiondataframe(expoverview, rdict, vollimits, rxndict, wellnum, userlimits, experiment):
    portionnum = 0
    prdf = pd.DataFrame()
    prmmoldf = pd.DataFrame()
    for portion in expoverview:
        # need the volume minimum and maximum and well count 
        reagentcount = 1
        reagenttotal = len(portion)
        # Determine from the chemicals and the remaining volume the maximum and minimum volume possible for the sobol method
        volmax = vollimits[portionnum][1]
        # unoptimized code that ensure that the previous reagents are considered and that the final reagent accurately fills to the minimum volume set by the users "fill to" requirement
        rdf = pd.DataFrame()
        mmoldf = pd.DataFrame()
        finalrdf = pd.DataFrame()
        finalmmoldf = pd.DataFrame()
        for reagent in portion:
            finalvolmin = vollimits[portionnum][0]
            volmin = 0
            # Unique set of requirements for the first entry
            if reagentcount == 1:
                # since all of the volume limits for the first draw are the same these can be treated as a bounded search sequence
                rvolmax, rvolmin = calcvollimit(userlimits, rdict, volmax, volmin, experiment, portion, reagent, wellnum)
                # Returns datafram of volumes of each reagent added to each experiment
                rdf = initialrdf(rvolmax, rvolmin, reagent, wellnum)
                # Returns mmol specified dataframe for each experiment, reagent, and chemical (<-- values are in the header) have been generated for this portion of the experiment
                mmoldf = mmolextension((rdf['Reagent%s (ul)' %reagent]), rdict, experiment, reagent)
                reagentcount+=1
                pass
            #operate within the available ranges taken from the previous constraints
            elif reagentcount < reagenttotal:
                # The constraints on the middle draws are more complicated and are dependent upon the first, a different sampling strategy must be used (i.e. this is not going to use sobol as the ranges are different for each)
                # Constrain the range based on volumne, reagent-chemical concentrations and user constraints
                rvolmaxdf, rvolmindf = calcvollimitdf(finalrdf, mmoldf, userlimits, rdict, volmax, volmin, experiment, portion, reagent, wellnum)
                # Since each volume maximum is different, need to sample the remaining reagents independently (thus different sampling) 
                rdf = rdfbuilder(rvolmaxdf, rvolmindf, reagent, wellnum)
                mmoldf = mmolextension((rdf['Reagent%s (ul)' %reagent]), rdict, experiment, reagent)
                reagentcount+=1
                pass
            # Ensure that the final round meets the lower bounds and upper bound total fill volume requirements of the user
            elif reagentcount == reagenttotal:
                if vollimits[portionnum][0] == vollimits[portionnum][1]:
#                    print(finalrdf.sum(axis=1))
                    rvolmaxdf, rvolmindf = calcvollimitdf(finalrdf, mmoldf, userlimits, rdict, volmax, volmin, experiment, portion, reagent, wellnum)
                    reagentname = "Reagent%s (ul)" %reagent
                    rdf = pd.DataFrame(rvolmaxdf, columns=[reagentname])
                    mmoldf = mmolextension((rdf['Reagent%s (ul)' %reagent]), rdict, experiment, reagent)
                else:
                    rvolmaxdf, rvolmindf = calcvollimitdf(finalrdf, mmoldf, userlimits, rdict, volmax, volmin, experiment, portion, reagent, wellnum)
                    rvolmindf = ensuremin(rvolmindf, finalrdf, finalvolmin)
                    rdf = rdfbuilder(rvolmaxdf, rvolmindf, reagent, wellnum)
                    mmoldf = mmolextension((rdf['Reagent%s (ul)' %reagent]), rdict, experiment, reagent)
                reagentcount+=1
            else: 
                modlog.error("Fatal error.  Unable to effectively parse reagent%s in portion %s.  Please make sure that the selected values make chemical sense!" %(reagent, portion))
            finalrdf = pd.concat([finalrdf, rdf], axis=1)
            finalmmoldf = pd.concat([finalmmoldf, mmoldf], axis=1)
        prdf = pd.concat([prdf, finalrdf], axis=1)
        prmmoldf = pd.concat([prmmoldf, finalmmoldf], axis=1)
        portionnum+=1
    return(prdf, prmmoldf)

def chemicallist(rxndict):
    chemicallist = []
    for k,v in rxndict.items():
        if 'abbreviation' in k:
            name = k.split('m')[1].split('_')[0]
            chemicallist.append(name)
    return(chemicallist)

def finalmmolsums(chemicals, usedchems, mmoldf):
    finalsummedmmols = pd.DataFrame()
    for chemical in chemicals:
        cname = 'chemical%s' %chemical
        coutname = 'chemical%s [M]' %chemical  # The technical output of this function is a mmol, simplier to rename the columns here
        tempdf = pd.DataFrame()
        for header in mmoldf.columns:
            if cname in header:
                tempdf = pd.concat([tempdf, mmoldf[header]], axis=1)
        summedmmols = pd.DataFrame(tempdf.sum(axis=1))
        summedmmols.columns = [coutname]
        finalsummedmmols = pd.concat([finalsummedmmols, summedmmols], axis=1)
    finalsummedmmols.fillna(value=0, inplace=True) # Total mmmols added of each chemical in previous reagent additions
    return(finalsummedmmols)

def preprocess(chemdf, rxndict, edict, rdict, climits):
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
    clist = (chemicallist(rxndict))
    # Final nominal molarity for each reagent in each well
    emsumdf = finalmmolsums(clist, clist, ermmoldf) # Returns incorrectly labeled columns, we used these immediately and convert to the correct units
    emsumdf = emsumdf.divide(erdf.sum(axis=1), axis='rows')*1000
    if rxndict['plotter_on'] == 1:
        if 1 <= rxndict['ExpWorkflowVer'] < 2:
            plotter.plotmewf1(emsumdf, rxndict)
        else:
            modlog.warning("Plot has been enabled, but no workflow specific plot has been programmed.  Not plot will be shown")
    else:
        pass
#    plotter.plotme(ReagentmmList[0],ReagentmmList[1], hold.tolist())
    #combine the experiments for the tray into one full set of volumes for all the wells on the plate
    modlog.info('Begin combining the experimental volume dataframes')
    return(erdf,ermmoldf,emsumdf)