import pandas as pd 
import logging

modlog = logging.getLogger('capture.generate.calcs')

def mmolextension(reagentdf, rdict, experiment, reagent):
    mmoldf = (pd.DataFrame(reagentdf))
    portionmmoldf = pd.DataFrame()
    for chemlistlocator, conc in (rdict['%s' %reagent].concs.items()):
        listposition = chemlistlocator.split('m')[1]
        chemnameint = int(listposition)
        truechemname = rdict['%s'%reagent].chemicals[chemnameint-1]
        newmmoldf = mmoldf * conc / 1000
        oldheaders = newmmoldf.columns
        newmmoldf.rename\
            (columns={'Reagent%s (ul)'%reagent:'mmol_experiment%s_reagent%s_%s' \
                %(experiment, reagent, truechemname)}, inplace=True)
        modlog.info('dataframe columns: %s renamed to: %s'%(oldheaders, newmmoldf.columns))
        portionmmoldf = pd.concat([portionmmoldf, newmmoldf], axis=1)
    return(portionmmoldf)

def finalmmolsums(chemicals, mmoldf):
    finalsummedmmols = pd.DataFrame()
    for chemical in chemicals:
        cname = '%s' %chemical
        coutname = '%s [M]' %chemical  # The technical output of this function is a mmol, simplier to rename the columns here
        tempdf = pd.DataFrame()
        for header in mmoldf.columns:
            if cname in header:
                tempdf = pd.concat([tempdf, mmoldf[header]], axis=1)
        summedmmols = pd.DataFrame(tempdf.sum(axis=1))
        summedmmols.columns = [coutname]
        finalsummedmmols = pd.concat([finalsummedmmols, summedmmols], axis=1)
    finalsummedmmols.fillna(value=0, inplace=True) # Total mmmols added of each chemical in previous reagent additions
    return(finalsummedmmols)