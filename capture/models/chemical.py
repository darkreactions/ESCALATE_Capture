import pandas as pd

import gspread
from capture.googleapi import googleio
from oauth2client.service_account import ServiceAccountCredentials

class perovskitechemical:
    def __init__(self, rxndict, chemdf):
        pass

def ChemicalData(chemsheetid, chemsheetworkbook):
    ### General Setup Information ###
    ##GSpread Authorization information
    print('Obtaining chemical information from Google Drive.. \n', end='')
    scope= ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc =gspread.authorize(credentials)
    chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
    ChemicalBook = gc.open_by_key(chemsheetid)
    chemicalsheet = ChemicalBook.get_worksheet(chemsheetworkbook)
    chemical_list = chemicalsheet.get_all_values()
    chemdf=pd.DataFrame(chemical_list, columns=chemical_list[0])
    chemdf=chemdf.iloc[1:]
    chemdf=chemdf.reset_index(drop=True)
    chemdf=chemdf.set_index(['Chemical Abbreviation'])
    return(chemdf)

def chemicallimits(rxndict):
    climits = {}
    for k,v in rxndict.items():
        if "chem" in k and "molarmin" in k:
            climits[k] = v
        if "chem" in k and "molarmax" in k:
            climits[k] = v
    return(climits)

def exp_chem_list(rdict):
    chemicalslist = []
    for reagentnum, reagentobject in rdict.items():
        for chemical in reagentobject.chemicals:
            if chemical in chemicalslist:
                pass
            else:
                chemicalslist.append(chemical)
    return(chemicalslist)
        