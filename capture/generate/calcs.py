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
