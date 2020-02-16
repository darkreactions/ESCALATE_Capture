"""ESCALATE Capture

Main point of entry for for EscalateCAPTURE
"""

import os
import sys
import ast
import xlrd
import logging
import argparse as ap

from log import init
from capture import specify
from capture import devconfig
import time
import json
from utils import globals, data_handling
import build_reagent_inventory



def iter_state_gen(rxndict, vardict):
    conc_dict = build_reagent_inventory.all_unique_experiments_v0('0048.perovskitedata.csv')
    with open('concdict.txt', 'w') as outfile:
        json.dump(conc_dict, outfile, indent=2) 
    #with open('concdict.txt') as json_file:
    #    conc_dict = json.load(json_file)
    for uid, my_dict in conc_dict.items():
        dict = my_dict['chemical_info']
        reagent_2_chemlist = [dict['inorganic'][1], dict['organic-1'][1], dict['solvent'][1]]
        rxndict['old_name'] = uid
        if 'null' in reagent_2_chemlist:
            print(f"RunID {uid} omitted due to unexpected preparation interface.  Manually update conc dict to include")
##            testtarget = [['PbI2', 'Me2NH2I', 'DMF'], ['PbI2', 'EtNH3I', 'GBL'],['PbI2', 'n-BuNH3I', 'GBL']]
##            if reagent_2_chemlist in testtarget:
        else:
            rxndict['Reagent1_chemical_list'] = [dict['solvent'][1]]
            # Reagent-chemical list update
            rxndict['Reagent2_chemical_list'] = reagent_2_chemlist
            rxndict['Reagent2_item1_formulaconc'] = dict['inorganic'][2]
            rxndict['Reagent2_item2_formulaconc'] = dict['organic-1'][2]
            reagent_3_chemlist = [dict['organic-2'][1], dict['solvent'][1]]
            rxndict['Reagent3_chemical_list'] = reagent_3_chemlist
            rxndict['Reagent3_item1_formulaconc'] = dict['organic-2'][2]

        escalatecapture(rxndict, vardict)


def escalatecapture(rxndict, vardict):
    """Point of entry into the data pipeline

    Manages processing calls to specify, generate, and prepare --> leads to execute

    :param rxndict: dictionary of Excel-specified params
    :param vardict: dictionary of dev-specified params
    :return None:
    """
    modlog = logging.getLogger('capture.escalatecapture')
    modlog.info("Initializing specify")
    specify.datapipeline(rxndict, vardict)


def linkprocess(linkfile):
    """TODO: what was this going to be for?"""
    return


def build_rxndict(rxnvarfile):
    """Read Template file and return a dict representation

    The rxndict is a mapping of Variables => Values (column B => column d) in the
    uncommented rows of the reaction excel file

    :param rxnvarfile: path to excel file containing reaction specification
    :return rxndict: dictionary representation of reaction specification
    """
    rxndict = {}
    varfile = rxnvarfile
    wb = xlrd.open_workbook(varfile)
    sheet = wb.sheet_by_name('WF1')
    for i in range(sheet.nrows):
        commentval = sheet.cell(i, 0).value
        if commentval == '#':
            continue
        else:
            cell_dict_value = sheet.cell(i, 3).value
            cell_dict_id = sheet.cell(i, 1).value
            cell_dict_type = sheet.cell(i, 4).value
            if cell_dict_id == "":
                pass
            if cell_dict_type == 'list':
                rxndict[cell_dict_id] = ast.literal_eval(cell_dict_value)
            else:
                rxndict[cell_dict_id.strip()] = cell_dict_value

    # cannot use globals.get_lab() here since it has not been set
    if rxndict['lab'] == 'MIT_PVLab':
        data_handling.get_user_actions(rxndict, sheet)
    return rxndict


if __name__ == "__main__":

    parser = ap.ArgumentParser(description='Generate experimental run data')
    parser.add_argument('Variables', type=str,
        help='Target xls file containing run information specified by the user\
             format should be "filename.xlsx"') 
    parser.add_argument('-s', '--ss', default=0, type=int, choices=[0, 1, 2],
        help='0 - quasi-random experiments generate, 1 - Generates stateset\
             for exp_1 user specified reagents, 2 - generate prototype run for\
             exp_1 user specified reagents') 
    parser.add_argument('-d', '--debug', default=0, type=int, choices=[0, 1],
        help='0 - complete run generation and upload to google drive,\
             1 - local debugging with no data upload,')

    args = parser.parse_args()
    challengeproblem = args.ss

    rxndict = build_rxndict(args.Variables)
    rxndict['challengeproblem'] = challengeproblem
    # vardict will hold variables configured by developers
    vardict = {
        'exefilename': args.Variables,
        'RoboVersion': devconfig.RoboVersion,
        'challengeproblem': challengeproblem,
        'debug': args.debug,
        'volspacing': devconfig.volspacing,
        'maxreagentchemicals': devconfig.maxreagentchemicals,
        'lab_vars': devconfig.lab_vars,
        'lab': rxndict['lab']
    }

    globals.set_lab(rxndict['lab'])

    init.runuidgen(rxndict, vardict)

    loggerfile = init.buildlogger(rxndict)
    rxndict['logfile'] = loggerfile



    # log the initial state of the run
    init.initialize(rxndict, vardict)

    iter_state_gen(rxndict, vardict)
    # TODO: >>>> insert variable tests here <<<<


