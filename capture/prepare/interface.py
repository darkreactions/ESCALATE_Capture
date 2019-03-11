import gspread
from oauth2client.service_account import ServiceAccountCredentials
from capture.googleapi import googleio

### File preparation --- Main Code Body ###
##Updates all of the run data information and creates the empty template for amine information
def PrepareDirectory(uploadlist, secfilelist, prepdict, rxndict, rdict, vardict):
    ### Directory and file collection handling###
    ##Generates new working directory with updated templates, return working folder ID
    scope= ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc =gspread.authorize(credentials)
    tgt_folder_id='11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe' #Target Folder for debugging
    PriDir=googleio.DriveCreateFolder(rxndict['RunID'], tgt_folder_id)
    file_dict=googleio.DriveAddTemplates(PriDir, rxndict['RunID'])
    print('Writing final values to experimental data entry form.....')
    # This is hardcoded as we don't know how long / much time we want to invest in developing an extensible interface.  
    # Will need a new version for WF3, likely.
    for key,val in file_dict.items(): 
        if "ExpDataEntry" in key: #Experimentalsheet = gc.open_bysearches for ExpDataEntry Form to get id
            sheetobject = gc.open_by_key(val).sheet1
#            print(sheetobject.get_all_values()) # Uncomment this to see some of the power of gspread
#            cell_list = sheetobject.range('B15:C30')
#            for cell in cell_list:
#                print(cell.label)
            # Direct writing by grouping until generalizing, minimum viable project
            # Reaction information
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
    secfold_name = "%s_subdata" %rxndict['RunID']
    secdir = googleio.DriveCreateFolder(secfold_name, PriDir)
    googleio.GupFile(PriDir, secdir, secfilelist, uploadlist, rxndict['RunID'], rxndict['logfile'])

def PrepareDirectoryCP(uploadlist, secfilelist, runID, logfile, rdict):
    scope= ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc =gspread.authorize(credentials)
    tgt_folder_id='11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe' #Target Folder for debugging
    PriDir=googleio.DriveCreateFolder(runID, tgt_folder_id)
    file_dict=googleio.DriveAddTemplates(PriDir, runID)
    subfold_name = "%s_submissions" %runID
    subdir = googleio.DriveCreateFolder(subfold_name, PriDir)
    secfold_name = "%s_subdata" %runID
    secdir = googleio.DriveCreateFolder(secfold_name, PriDir)
    googleio.GupFile(PriDir, secdir, secfilelist, uploadlist, runID, logfile)