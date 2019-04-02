import pandas as pd


def conreag(rxndict, rdf, chemdf, rdict, robotfile):
    #Constructing output information for creating the experimental excel input sheet
    solventvolume=rdf['Reagent1 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockAvolume=rdf['Reagent2 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid6=rdf['Reagent6 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid7=rdf['Reagent7 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run

    PbI2mol=(stockAvolume/1000/1000*rxndict['reag2_target_conc_chemical2'])
    PbI2mass=(PbI2mol*float(chemdf.loc["PbI2", "Molecular Weight (g/mol)"]))
    StockAAminePercent=(rxndict['reag2_target_conc_chemical3']/rxndict['reag2_target_conc_chemical2'])
    aminemassA=(stockAvolume/1000/1000*rxndict['reag2_target_conc_chemical2']*StockAAminePercent*float(chemdf.loc[rxndict['chem3_abbreviation'], "Molecular Weight (g/mol)"]))
    stockBvolume=rdf['Reagent3 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    Aminemol=(stockBvolume/1000/1000*rxndict['reag3_target_conc_chemical3'])
    aminemassB=(Aminemol*float(chemdf.loc[rxndict['chem3_abbreviation'], "Molecular Weight (g/mol)"]))

    #The following section handles and output dataframes to the format required by the robot.xls file.  File type is very picky about white space and formatting.  
    FinalAmountArray_hold={}
    FinalAmountArray_hold['solvent_volume']=((solventvolume/1000).round(2))
    FinalAmountArray_hold['pbi2mass']=(PbI2mass.round(2))
    FinalAmountArray_hold['Aaminemass']=((aminemassA.round(2)))
    FinalAmountArray_hold['Afinalvolume']=((stockAvolume/1000).round(2))
    FinalAmountArray_hold['Baminemass']=(aminemassB.round(2))
    FinalAmountArray_hold['Bfinalvolume']=((stockBvolume/1000).round(2))
    FinalAmountArray_hold['FA6']=((stockFormicAcid6/1000).round(2))
    FinalAmountArray_hold['FA7']=((stockFormicAcid7/1000).round(2))
    return(FinalAmountArray_hold)

