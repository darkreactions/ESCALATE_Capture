import logging
import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from capture.googleapi import googleio

modlog = logging.getLogger('capture.prepare.interface')

def conreag(rxndict, rdf, chemdf, rdict):
    #Constructing output information for creating the experimental excel input sheet
    for reagentnum, reagentobject in rdict.items():
        if reagentobject.ispurebool == 1:
            pass
            #(reagentobject.chemicals)
        else:
            pass

    solventvolume=rdf['Reagent1 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockAvolume=rdf['Reagent2 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid6=rdf['Reagent6 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    stockFormicAcid7=rdf['Reagent7 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run

    PbI2mol=(stockAvolume/1000/1000*rxndict['Reagent2_item1_formulaconc'])
    PbI2mass=(PbI2mol*float(chemdf.loc["PbI2", "Molecular Weight (g/mol)"]))
    StockAAminePercent=(rxndict['Reagent2_item2_formulaconc']/rxndict['Reagent2_item1_formulaconc'])
    aminemassA=(stockAvolume/1000/1000*rxndict['Reagent2_item1_formulaconc']*StockAAminePercent*float(chemdf.loc[rxndict['chem3_abbreviation'], "Molecular Weight (g/mol)"]))
    stockBvolume=rdf['Reagent3 (ul)'].sum()+rxndict['reagent_dead_volume']*1000 #Total volume of the stock solution needed for the robot run
    Aminemol=(stockBvolume/1000/1000*rxndict['Reagent3_item1_formulaconc'])
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
    
def sumreagents(erdf, deadvolume):
    reagent_volume_dict = {}
    for header in erdf.columns:
        reagent_volume = erdf[header].sum() + deadvolume
        reagentname = header.split(' ')[0]
        reagent_volume_dict[reagentname] = reagent_volume
    return(reagent_volume_dict)

def preparationdf(rxndict, chemicalnamedf, sumreagentsdict, solventlist, maxreagentchemicals, chemdf):
    ''' calculate the mass of each chemical return dataframe

    ''' 
    nominalsdf = pd.DataFrame()
    itemcount = 1
    for index, row in chemicalnamedf.iterrows():
        reagentname = row['reagentnames']
        chemabbr = row['chemabbr']
        if row['chemabbr'] ==  'Final Volume = ':
            itemcount = 1
            finalvolindex = index
            pass
        else:
            if chemabbr in solventlist:
                formulavol = (sumreagentsdict[reagentname]/1000).round(2)
                nominalsdf.loc[index, "nominal_amount"] = formulavol
                itemcount+=1
            elif chemabbr == 'null':
                nominalsdf.loc[index, "nominal_amount"] =  'null'
                itemcount+=1
                pass
            else:
                modlog.info(('Formula target was', chemabbr, reagentname, \
                    rxndict['%s_item%s_formulaconc' %(reagentname, itemcount)]))
                modlog.info((index, 'calc value = ', sumreagentsdict[reagentname]/1000/1000 * \
                    rxndict['%s_item%s_formulaconc' %(reagentname, itemcount)] * \
                    float(chemdf.loc["%s" %chemabbr, "Molecular Weight (g/mol)"])
                    ))
                nominalamount = (sumreagentsdict[reagentname]/1000/1000 * \
                    rxndict['%s_item%s_formulaconc' %(reagentname, itemcount)] * \
                    float(chemdf.loc["%s" %chemabbr, "Molecular Weight (g/mol)"])
                    ).round(2)
                nominalsdf.loc[index, "nominal_amount"] =  nominalamount
                itemcount+=1
        if itemcount == maxreagentchemicals:
            nominalsdf.loc[finalvolindex, "nominal_amount"] = formulavol.round(1)
            modlog.info((reagentname, "formula calculation complete"))
    nominalsdf.sort_index(inplace=True)
    print(nominalsdf)
    return(nominalsdf)
#    for reagentname, totalvol in sumreagentsdict.items():
#        reagentnamenum = (reagentname.split(' ')[0])



def chemicalnames(rxndict, rdict, chemdf, maxreagentchemicals):
    '''generates a list of chemical names for reagent interface

    :param chemdf:  Chemical data frame from google drive.  

    :returns: a list sized for export to version:: 3.0 interface
    '''
    chemicalnamelist = []
    reagentnamelist = []
    for reagentnum, reagentobject in rdict.items():
        count=0
        chemicalnamelist.append('Final Volume = ')
        reagentnamelist.append('Reagent%s' %reagentnum)
        for chemical in reagentobject.chemicals:
            chemicalname = rxndict['chem%s_abbreviation' %chemical]
            reagentnamelist.append('Reagent%s' %reagentnum)
            chemicalnamelist.append(chemicalname)
            count+=1
        while count < maxreagentchemicals:
            chemicalnamelist.append('null')
            reagentnamelist.append('Reagent%s' %reagentnum)
            count+=1
        else: pass
#    chemicalnamedf = pd.DataFrame(chemicalnamelist, columns=['Chemical Abbreviation (In order of addition)'])
    chemicalnamedf = pd.DataFrame(chemicalnamelist, columns=['chemabbr'])
    reagentnamedf = pd.DataFrame(reagentnamelist, columns=['reagentnames'])
    chemicalnamedf = pd.concat([chemicalnamedf, reagentnamedf], axis=1)
    return(chemicalnamedf)

def reagentupload(rxndict, vardict, erdf, rdict, chemdf, gc, val):
    ''' uploads information to google sheets reagent interface template

    requires all components of the experiment prep in order to calculate
    experiment --> reagent --> chemical relationships and present them 
    to the interface.  GC = gspread authentication, val = reagentinterface target
    UID

    .. version:: 3.0
    '''
    modlog.info('Starting reagent interface upload')
#    cell_list = sheetobject.range('B15:C30')
#    for cell in cell_list:
#        print(cell.label)
    # Reaction information
    chemicalnamedf = chemicalnames(rxndict, rdict, chemdf, vardict['maxreagentchemicals'])
    sumreagentsdict = sumreagents(erdf, rxndict['reagent_dead_volume']*1000)
    nominalsdf = preparationdf(rxndict, chemicalnamedf, sumreagentsdict, vardict['solventlist'], \
        vardict['maxreagentchemicals'], chemdf)
    
    prepdict =  conreag(rxndict, erdf, chemdf, rdict)
    sheetobject = gc.open_by_key(val).sheet1
    sheetobject.update_acell('B2', rxndict['date']) #row, column, replacement in experimental data entry form
    sheetobject.update_acell('B3', rxndict['time'])
    sheetobject.update_acell('B4', rxndict['lab'])
    sheetobject.update_acell('B6', rxndict['RunID'])
    sheetobject.update_acell('B7', rxndict['ExpWorkflowVer'])
    sheetobject.update_acell('B8', vardict['RoboVersion'])
    sheetobject.update_acell('B9', rxndict['challengeproblem'])

    # Notes section - blank values as default
    sheetobject.update_acell('B10', 'null')
    sheetobject.update_acell('B11', 'null')
    sheetobject.update_acell('B12', 'null')

    # Reagent preparation
     #Reagent 2
    sheetobject.update_acell('D4', rdict['2'].preptemperature)
    sheetobject.update_acell('E4', rdict['2'].prepstirrate)
    sheetobject.update_acell('F4', rdict['2'].prepduration)
     #Reagent 3
    sheetobject.update_acell('D5', rdict['3'].preptemperature)
    sheetobject.update_acell('E5', rdict['3'].prepstirrate)
    sheetobject.update_acell('F5', rdict['3'].prepduration)
    # Reagent 1 - use all values present if possible
    sheetobject.update_acell('B16', rxndict['chem%s_abbreviation'%rdict['1'].chemicals[0]])
    sheetobject.update_acell('C15', prepdict['solvent_volume']) #nominal final
    sheetobject.update_acell('C16', prepdict['solvent_volume']) #chemical added
    sheetobject.update_acell('E16', 'milliliter') #label for volume based measurements, units for GBL
    sheetobject.update_acell('H15', rdict['1'].prerxntemp)
    # Reagent 2 - Use all values present if possible (i.e. if a reagent has information make sure to encode it!)
    sheetobject.update_acell('C19', prepdict['Afinalvolume']) # final nominal
    sheetobject.update_acell('B20', rxndict['chem%s_abbreviation'%rdict['2'].chemicals[0]])
    sheetobject.update_acell('B21', rxndict['chem%s_abbreviation'%rdict['2'].chemicals[1]])
    sheetobject.update_acell('B22', rxndict['chem%s_abbreviation'%rdict['2'].chemicals[2]])
    sheetobject.update_acell('C20', prepdict['pbi2mass'])
    sheetobject.update_acell('E20', 'gram') #label for solid based measurements, units for pbi2
    sheetobject.update_acell('C21', prepdict['Aaminemass'])
    sheetobject.update_acell('E21', 'gram') #label for solid based measurements, units for pbi2
    sheetobject.update_acell('C22', prepdict['Afinalvolume'])
    sheetobject.update_acell('E22', 'milliliter') #label for volume based measurements, units for GBL
    sheetobject.update_acell('H19', rdict['2'].prerxntemp)
    # Reagent 3 - Use all values present if possible (i.e. if a reagent has information make sure to encode it!)
    sheetobject.update_acell('C23', prepdict['Bfinalvolume'])
    sheetobject.update_acell('B24', rxndict['chem%s_abbreviation'%rdict['3'].chemicals[0]])
    sheetobject.update_acell('B25', rxndict['chem%s_abbreviation'%rdict['3'].chemicals[1]])
    sheetobject.update_acell('C24', prepdict['Baminemass'])
    sheetobject.update_acell('E24', 'gram') #label for solid based measurements, units for pbi2
    sheetobject.update_acell('C25', prepdict['Bfinalvolume'])
    sheetobject.update_acell('E25', 'milliliter') #label for volume based measurements, units for GBL
    sheetobject.update_acell('H23', rdict['3'].prerxntemp)
    # Reagent 4 - Use all values present if possible (i.e. if a reagent has information make sure to encode it!)
    # Reagent 6 - Use all values present if possible (i.e. if a reagent has information make sure to encode it!)
    sheetobject.update_acell('B36', rxndict['chem%s_abbreviation'%rdict['6'].chemicals[0]])
    sheetobject.update_acell('C35', prepdict['FA6'])
    sheetobject.update_acell('C36', prepdict['FA6'])
    sheetobject.update_acell('E36', 'milliliter') #label for volume based measurements, units for GBL
    sheetobject.update_acell('H35', rdict['6'].prerxntemp)
    # Reagent 7 - Use all values present if possible (i.e. if a reagent has information make sure to encode it!)
    sheetobject.update_acell('B40', rxndict['chem%s_abbreviation'%rdict['7'].chemicals[0]])
    sheetobject.update_acell('C39', prepdict['FA7'])
    sheetobject.update_acell('C40', prepdict['FA7'])
    sheetobject.update_acell('E40', 'milliliter') #label for volume based measurements, units for GBL
    sheetobject.update_acell('H39', rdict['7'].prerxntemp)

def PrepareDirectoryCP(uploadlist, secfilelist, runID, logfile, rdict, targetfolder):
    scope= ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc =gspread.authorize(credentials)
    tgt_folder_id= targetfolder
    PriDir=googleio.DriveCreateFolder(runID, tgt_folder_id)
    file_dict=googleio.DriveAddTemplates(PriDir, runID, targetfolder)
    subfold_name = "%s_submissions" %runID
    subdir = googleio.DriveCreateFolder(subfold_name, PriDir)
    secfold_name = "%s_subdata" %runID
    secdir = googleio.DriveCreateFolder(secfold_name, PriDir)
    googleio.GupFile(PriDir, secdir, secfilelist, uploadlist, runID, logfile)