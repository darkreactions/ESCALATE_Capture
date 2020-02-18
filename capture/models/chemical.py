import pandas as pd
import os

import gspread
from capture.googleapi import googleio
from oauth2client.service_account import ServiceAccountCredentials

class perovskitechemical:
    def __init__(self, rxndict, chemdf):
        pass

def build_chemdf(chemsheetid, chemsheetworkbook, debug_bool):
    """Get the chemical sheet from the chemical inventory

    :param chemsheetid:       todo this is a workbook (and unused)
    :param chemsheetworkbook: todo this is a sheet    (Rest in peace Ian Pendletoon)
    :return:
    """

    print('Obtaining chemical information from Google Drive.. \n', end='')
    if not os.path.exists('chemdf.csv'):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
        gc = gspread.authorize(credentials)

        ChemicalBook = gc.open_by_key(chemsheetid)
        chemicalsheet = ChemicalBook.get_worksheet(chemsheetworkbook)
        chemical_list = chemicalsheet.get_all_values()

        chemdf = pd.DataFrame(chemical_list, columns=chemical_list[0])
        chemdf = chemdf.iloc[1:]
        chemdf = chemdf.reset_index(drop=True)
        chemdf = chemdf.set_index(['Chemical Abbreviation'])
        if debug_bool > 0:
            chemdf.to_csv('chemdf.csv')
    else:
        chemdf = pd.read_csv('chemdf.csv')
        chemdf = chemdf.set_index(['Chemical Abbreviation'])
    return chemdf


def chemicallimits(rxndict):
    """Return the molarmins and maxes for each chemical in the run

    :param rxndict:
    :return:
    """
    climits = {}
    for k, v in rxndict.items():
        if "chem" in k and "molarmin" in k:
            climits[k] = v
        if "chem" in k and "molarmax" in k:
            climits[k] = v
    return climits


def exp_chem_list(rdict):
    """extract the chemicals that were used.
    :param rdict: see DataStructures_README.md
    :return: a set of the chemicals used in all the experiments
    """
    chemicalslist = []
    for reagentnum, reagentobject in rdict.items():
        for chemical in reagentobject.chemicals:
            if chemical in chemicalslist:
                pass
            else:
                chemicalslist.append(chemical)
    return chemicalslist
