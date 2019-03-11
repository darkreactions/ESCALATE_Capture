import pandas as pd

import gspread
from capture.googleapi import googleio
from oauth2client.service_account import ServiceAccountCredentials

class perovskitechemical:
    def __init__(self, rxndict, chemdf):
        pass

def ChemicalData():
    ### General Setup Information ###
    ##GSpread Authorization information
    print('Obtaining chemical information from Google Drive.. \n', end='')
    scope= ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc =gspread.authorize(credentials)
    chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
    ChemicalBook = gc.open_by_key(chemsheetid)
    chemicalsheet = ChemicalBook.get_worksheet(0)
    chemical_list = chemicalsheet.get_all_values()
    chemdf=pd.DataFrame(chemical_list, columns=chemical_list[0])
    chemdf=chemdf.iloc[1:]
    chemdf=chemdf.reset_index(drop=True)
    chemdf=chemdf.set_index(['Chemical Abbreviation'])
    return(chemdf)