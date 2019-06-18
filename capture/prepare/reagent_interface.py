import logging
import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from capture.googleapi import googleio

modlog = logging.getLogger('capture.prepare.interface')


def sumreagents(erdf, deadvolume):
    reagent_volume_dict = {}
    for header in erdf.columns:
        reagent_volume = erdf[header].sum() + deadvolume
        reagentname = header.split(' ')[0]
        reagent_volume_dict[reagentname] = reagent_volume
    return(reagent_volume_dict)


def preparationdf(rdict,
                  chemicalnamedf,
                  sumreagentsdict,
                  liquidlist,
                  maxreagentchemicals,
                  chemdf):
    ''' calculate the mass of each chemical return dataframe

    TODO: write out nominal molarity to google sheets, see issue#52

    :param chemdf:  Chemical data frame from google drive.

    :returns: a dataframe sized for export to version:: 3.0 interface
    '''
    nominalsdf = pd.DataFrame()
    itemcount = 1
    chemicalnamedf.sort_index(inplace=True)
    for index, row in chemicalnamedf.iterrows():
        reagentname = row['reagentnames']
        chemabbr = row['chemabbr']
        if row['chemabbr'] ==  'Final Volume = ':
            formulavollist = []
            formulavol = 'null'
            itemcount = 1
            finalvolindex = index
            pass
        else:
            # stock solutions should be summed for final total volume
            if chemabbr in liquidlist or chemabbr == 'FAH':  # todo dejank
                formulavol = (sumreagentsdict[reagentname]/1000).round(2)
                formulavollist.append(formulavol)
                nominalsdf.loc[index, "nominal_amount"] = formulavol
                nominalsdf.loc[index, "Unit"] = 'milliliter'
                itemcount+=1
            elif chemabbr == 'null':
                nominalsdf.loc[index, "nominal_amount"] =  'null'
                nominalsdf.loc[index, "Unit"] = 'null'
                nominalsdf.loc[index, "actualsnull"] = 'null'
                itemcount+=1
                pass
            else:
                #calculate reagent amounts from formula
                reagentnum = str(reagentname.split('t')[1])
#                print(rdict[reagentnum].concs['conc_item%s'%(itemcount)])
                modlog.info(('Formula target was', chemabbr, reagentname, \
                    rdict[reagentnum].concs['conc_item%s' %(itemcount)]))
                modlog.info(('row index =', index, 'calc value = ', sumreagentsdict[reagentname]/1000/1000 * \
                    rdict[reagentnum].concs['conc_item%s' %(itemcount)] * \
                    float(chemdf.loc["%s" %chemabbr, "Molecular Weight (g/mol)"])
                    ))
                nominalamount = (sumreagentsdict[reagentname]/1000/1000 * \
                    rdict[reagentnum].concs['conc_item%s' %(itemcount)] * \
                    float(chemdf.loc["%s" %chemabbr, "Molecular Weight (g/mol)"])
                    ).round(2)
                nominalsdf.loc[index, "nominal_amount"] =  nominalamount
                nominalsdf.loc[index, "Unit"] = 'gram'
                itemcount+=1
        if itemcount == (maxreagentchemicals+1):
            if len(formulavollist) > 0:
                nominalsdf.loc[finalvolindex, "nominal_amount"] = sum(formulavollist)
                nominalsdf.loc[finalvolindex, "Unit"] = 'milliliter'
            else: 
                nominalsdf.loc[finalvolindex, "nominal_amount"] = formulavol
                nominalsdf.loc[finalvolindex, "Unit"] = 'null'
                nominalsdf.loc[finalvolindex, "actualsnull"] = 'null'
            modlog.info((reagentname, "formula calculation complete"))
    nominalsdf.sort_index(inplace=True)
    return(nominalsdf)
#    for reagentname, totalvol in sumreagentsdict.items():
#        reagentnamenum = (reagentname.split(' ')[0])



def chemicalnames(rxndict, rdict, chemdf, maxreagentchemicals, maxreagents):
    '''generates a dataframe of chemical names for reagent interface

    :param chemdf:  Chemical data frame from google drive.  

    :returns: a dataframe sized for export to version:: 3.0 interface
    '''
    chemicalnamelist = []
    reagentnamelist = []
    holdreagentnum = 1
    for reagentnum in sorted(rdict.keys()):
        #ensure any reagents not used have placeholders
        while int(reagentnum) > holdreagentnum:
            chemicalnamelist.append('Final Volume = ')
            chemicalnamelist.extend(['null'] * maxreagentchemicals)
            maxinterfaceslots = maxreagentchemicals + 1
            reagentnamelist.extend(['Reagent%s' %holdreagentnum] * maxinterfaceslots)
            holdreagentnum = holdreagentnum+1
        else:
            count=0
            holdreagentnum = int(reagentnum)+1
            chemicalnamelist.append('Final Volume = ')
            reagentnamelist.append('Reagent%s' %reagentnum)
            for chemical in rdict[reagentnum].chemicals:
                chemicalnamelist.append(chemical)
                reagentnamelist.append('Reagent%s' %reagentnum)
                count+=1
            while count < maxreagentchemicals:
                chemicalnamelist.append('null')
                reagentnamelist.append('Reagent%s' %reagentnum)
                count+=1
            else: pass
    chemicalnamedf = pd.DataFrame(chemicalnamelist, columns=['chemabbr'])
    reagentnamedf = pd.DataFrame(reagentnamelist, columns=['reagentnames'])
    chemicalnamedf = pd.concat([chemicalnamedf, reagentnamedf], axis=1)
    return(chemicalnamedf)

def reagent_data_prep(rxndict, vardict, erdf, rdict, chemdf):
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
    # Prepare the dataframe for export to the gsheets interface 
    chemicalnamedf = chemicalnames(rxndict, rdict, chemdf, vardict['maxreagentchemicals'], \
        vardict['max_robot_reagents'])
    sumreagentsdict = sumreagents(erdf, rxndict['reagent_dead_volume']*1000)
    nominalsdf = preparationdf(rdict, chemicalnamedf, sumreagentsdict, vardict['solventlist'], \
        vardict['maxreagentchemicals'], chemdf)
    finalexportdf = (pd.concat([chemicalnamedf, nominalsdf], axis=1))
    return(finalexportdf)

def reagent_interface_upload(rxndict, vardict, finalexportdf, gc, val):
    ''' upload rxndict, finalexportdf to gc target, returns the used gsheets object 

    '''
    #begin export of the dataframe
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

    #adaptive row specification (easier updates)
    rowstart = vardict['reagent_interface_amount_startrow']
    rowend = len(finalexportdf.index) + rowstart-1

    # Chemical abbreviations
    chemlabeltarget = sheetobject.range('B%s:B%s'%(rowstart, rowend))
    chemlabeldf = finalexportdf['chemabbr']
    chemlabellist = chemlabeldf.values.tolist()
    count = 0
    for cell in chemlabeltarget:
        cell.value = chemlabellist[count]
        count+=1
    sheetobject.update_cells(chemlabeltarget)

    #Formula amounts of materials to generate the objects
    amounttarget = sheetobject.range('C%s:C%s'%(rowstart, rowend))
    amountdf = finalexportdf['nominal_amount']
    amountlist = amountdf.values.tolist()
    count = 0
    for cell in amounttarget:
        cell.value = amountlist[count]
        count+=1
    sheetobject.update_cells(amounttarget)

    # export unit labels
    unittarget = sheetobject.range('E%s:E%s'%(rowstart, rowend))
    unitdf = finalexportdf['Unit']
    unitlist = unitdf.values.tolist()
    count = 0
    for cell in unittarget:
        cell.value = unitlist[count]
        count+=1
    sheetobject.update_cells(unittarget)

    #correctly send out nulls for "actuals" column
    nulltarget = sheetobject.range('D%s:D%s'%(rowstart, rowend))
    nulldf = finalexportdf['actualsnull']
    nulllist = nulldf.values.tolist()
    nlsexport = [x if x == 'null' else '' for x in nulllist]
    count = 0
    for cell in nulltarget:
        cell.value = nlsexport[count]
        count+=1
    sheetobject.update_cells(nulltarget)

    return(sheetobject)

def reagent_prep_pipeline(rdict, sheetobject, maxreagents):
    uploadtarget = sheetobject.range('D3:F9')
    uploadlist = []
    reagentcount = 1
    for reagentnum, reagentobject in rdict.items():
        while int(reagentnum) > reagentcount:
            uploadlist.append('null')
            uploadlist.append('null')
            uploadlist.append('null')
            reagentcount += 1
        if int(reagentnum) == reagentcount:
            uploadlist.append(reagentobject.preptemperature)
            uploadlist.append(reagentobject.prepstirrate)
            uploadlist.append(reagentobject.prepduration)
            reagentcount += 1
        #else:
        #    uploadlist.append('null')
        #    uploadlist.append('null')
        #    uploadlist.append('null')
        #    reagentcount += 1
#    for reagentnum, reagentobject in rdict.items():
#    for reagentnum, reagentobject in rdict.items():
    count = 0
    for cell in uploadtarget:
        cell.value = uploadlist[count]
        count+=1
    sheetobject.update_cells(uploadtarget)

    # Reagent 1 - use all values present if possible
    try:
        sheetobject.update_acell('H15', rdict['1'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H15', 'null')

    #Reagent 2
    try:
        sheetobject.update_acell('H19', rdict['2'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H19', 'null')

    #Reagent 3
    try:
        sheetobject.update_acell('H23', rdict['3'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H23', 'null')

    # Reagent 4
    try:
        sheetobject.update_acell('H27', rdict['4'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H27', 'null')

    # Reagent 5 
    try:
        sheetobject.update_acell('H31', rdict['4'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H31', 'null')

    # Reagent 6 
    try:
        sheetobject.update_acell('H35', rdict['6'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H35', 'null')

    # Reagent 7 
    try:
        sheetobject.update_acell('H39', rdict['7'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H39', 'null')

def PrepareDirectoryCP(uploadlist, secfilelist, runID, logfile, rdict, targetfolder):
#    scope= ['https://spreadsheets.google.com/feeds']
#    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
#    gc =gspread.authorize(credentials)
    tgt_folder_id= targetfolder
    PriDir=googleio.DriveCreateFolder(runID, tgt_folder_id)
    googleio.DriveAddTemplates(PriDir, runID, []) # copies metadata from current template (leaves the rest)
    secfold_name = "%s_subdata" %runID
    secdir = googleio.DriveCreateFolder(secfold_name, PriDir)
    googleio.GupFile(PriDir, secdir, secfilelist, uploadlist, runID, logfile)