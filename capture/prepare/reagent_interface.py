"""
TODO Pendletoon, doc this whole module
"""

import logging
import pandas as pd

from capture.devconfig import max_robot_reagents
from capture.devconfig import maxreagentchemicals
from capture.devconfig import reagent_interface_amount_startrow

modlog = logging.getLogger('capture.prepare.interface')


def get_reagent_target_volumes(erdf, deadvolume):
    """Target volumes for reagent preparation as dictionary"""
    reagent_target_volumes = {}
    for reagent in erdf.columns:
        reagent_volume = erdf[reagent].sum() + deadvolume
        reagentname = reagent.split(' ')[0]
        reagent_target_volumes[reagentname] = reagent_volume
    return reagent_target_volumes


def build_nominals_df(rdict,
                      chemicalnamedf,
                      sumreagentsdict,
                      liquidlist,
                      maxreagentchemicals,
                      chemdf):
    ''' calculate the mass of each chemical return dataframe

    TODO: write out nominal molarity to google sheets, see issue#52

    :param chemdf:  Chemical data frame from google drive.
    :returns: a dataframe sized for export to version 2.x interface
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
                nominalsdf.loc[index, "nominal_amount"] = 'null'
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
    return nominalsdf



def build_chemical_names_df(rdict, maxreagentchemicals):
    """generates a dataframe of chemical names for reagent interface

    :param chemdf:  Chemical data frame from google drive.  

    :returns: a dataframe sized for export to version:: 3.0 interface
    """
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
            holdreagentnum += 1
        else:
            count = 0
            holdreagentnum = int(reagentnum)+1
            chemicalnamelist.append('Final Volume = ')
            reagentnamelist.append('Reagent%s' %reagentnum)
            for chemical in rdict[reagentnum].chemicals:
                chemicalnamelist.append(chemical)
                reagentnamelist.append('Reagent%s' %reagentnum)
                count += 1
            while count < maxreagentchemicals:
                chemicalnamelist.append('null')
                reagentnamelist.append('Reagent%s' %reagentnum)
                count += 1
    chemicalnamedf = pd.DataFrame(chemicalnamelist, columns=['chemabbr'])
    reagentnamedf = pd.DataFrame(reagentnamelist, columns=['reagentnames'])
    chemicalnamedf = pd.concat([chemicalnamedf, reagentnamedf], axis=1)
    return chemicalnamedf

def build_reagent_spec_df(rxndict, vardict, erdf, rdict, chemdf):
    """Build the dataframe for the bottom portion of the reagent preparation_interface

    :param rxndict:
    :param vardict:
    :param erdf:
    :param rdict:
    :param chemdf:
    :return:
    """
    modlog.info('Starting reagent interface upload')
    chemical_names_df = build_chemical_names_df(rdict, vardict['maxreagentchemicals'])
    reagent_target_volumes = get_reagent_target_volumes(erdf, rxndict['reagent_dead_volume'] * 1000)
    nominals_df = build_nominals_df(rdict, chemical_names_df, reagent_target_volumes,
                                    vardict['solventlist'], vardict['maxreagentchemicals'], chemdf)
    reagent_spec_df = pd.concat([chemical_names_df, nominals_df], axis=1)
    return reagent_spec_df


def upload_reagent_interface(rxndict, vardict, rdict, finalexportdf, gc, uid):
    sheet = gc.open_by_key(uid).sheet1
    upload_reagent_prep_info(rdict, sheet)
    upload_run_information(rxndict, vardict, sheet)
    upload_reagent_specifications(rxndict, vardict, finalexportdf, sheet)


def upload_run_information(rxndict, vardict, sheet):
    sheet.update_acell('B2', rxndict['date']) #row, column, replacement in experimental data entry form
    sheet.update_acell('B3', rxndict['time'])
    sheet.update_acell('B4', rxndict['lab'])
    sheet.update_acell('B6', rxndict['RunID'])
    sheet.update_acell('B7', rxndict['ExpWorkflowVer'])
    sheet.update_acell('B8', vardict['RoboVersion'])
    sheet.update_acell('B9', rxndict['challengeproblem'])

    # Notes section - blank values as default
    sheet.update_acell('B10', 'null')
    sheet.update_acell('B11', 'null')
    sheet.update_acell('B12', 'null')

def upload_reagent_specifications(rxndict, vardict, finalexportdf, sheet):
    ''' upload rxndict, finalexportdf to gc target, returns the used gsheets object 

    '''
    #adaptive row specification (easier updates)
    rowstart = vardict['reagent_interface_amount_startrow']
    rowend = len(finalexportdf.index) + rowstart-1

    # Chemical abbreviations
    # TODO MIT: Abstract this as funciton: df col, sheet_uid, rowstart = 1, rowend = n_exp
    chemlabeltarget = sheet.range('B%s:B%s' % (rowstart, rowend))
    chemlabeldf = finalexportdf['chemabbr']
    chemlabellist = chemlabeldf.values.tolist()
    count = 0
    for cell in chemlabeltarget:
        cell.value = chemlabellist[count]
        count+=1
    sheet.update_cells(chemlabeltarget)

    #Formula amounts of materials to generate the objects
    amounttarget = sheet.range('C%s:C%s' % (rowstart, rowend))
    amountdf = finalexportdf['nominal_amount']
    amountlist = amountdf.values.tolist()
    count = 0
    for cell in amounttarget:
        cell.value = amountlist[count]
        count+=1
    sheet.update_cells(amounttarget)

    # export unit labels
    unittarget = sheet.range('E%s:E%s' % (rowstart, rowend))
    unitdf = finalexportdf['Unit']
    unitlist = unitdf.values.tolist()
    count = 0
    for cell in unittarget:
        cell.value = unitlist[count]
        count+=1
    sheet.update_cells(unittarget)

    #correctly send out nulls for "actuals" column
    nulltarget = sheet.range('D%s:D%s' % (rowstart, rowend))
    nulldf = finalexportdf['actualsnull']
    nulllist = nulldf.values.tolist()
    nlsexport = [x if x == 'null' else '' for x in nulllist]
    count = 0
    for cell in nulltarget:
        cell.value = nlsexport[count]
        count+=1
    sheet.update_cells(nulltarget)

    null_start = rowend+1
    null_end = max_robot_reagents * (maxreagentchemicals + 1) + \
               reagent_interface_amount_startrow + 1
    nulltarget2 = sheet.range('D%s:D%s' % (null_start, null_end))
    for cell in nulltarget2:
        cell.value = 'null'
    sheet.update_cells(nulltarget2)


def upload_reagent_prep_info(rdict, sheetobject):
    uploadtarget = sheetobject.range('D3:F9')
    uploadlist = []
    reagentcount = 1
    for reagentnum, reagentobject in rdict.items():
        while int(reagentnum) > reagentcount:
            uploadlist.extend(['null']*3)
            reagentcount += 1
        if int(reagentnum) == reagentcount:
            uploadlist.append(reagentobject.preptemperature)
            uploadlist.append(reagentobject.prepstirrate)
            uploadlist.append(reagentobject.prepduration)
            reagentcount += 1
    count = 0
    for cell in uploadtarget:
        try:
            cell.value = uploadlist[count]
            count += 1  
        except:
            count += 1
    sheetobject.update_cells(uploadtarget)

    # Reagent 1 - use all values present if possible
    try:
        sheetobject.update_acell('H16', rdict['1'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H16', 'null')

    #Reagent 2
    try:
        sheetobject.update_acell('H21', rdict['2'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H21', 'null')

    #Reagent 3
    try:
        sheetobject.update_acell('H26', rdict['3'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H26', 'null')

    # Reagent 4
    try:
        sheetobject.update_acell('H31', rdict['4'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H31', 'null')

    # Reagent 5 
    try:
        sheetobject.update_acell('H36', rdict['4'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H36', 'null')

    # Reagent 6 
    try:
        sheetobject.update_acell('H41', rdict['6'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H41', 'null')

    # Reagent 7 
    try:
        sheetobject.update_acell('H46', rdict['7'].prerxntemp)
    except Exception:
        sheetobject.update_acell('H46', 'null')
