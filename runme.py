import os
import sys
import ast
import xlrd
import logging
import argparse as ap

from log import init
from capture import specify
from capture import devconfig

def escalatecapture(rxndict,vardict):
    ''' Subsequent calls to each portion of the escalate_capture pipeline

    Manages processing calls to specify, generate, and prepare --> leads to execute
    '''
    modlog = logging.getLogger('capture.escalatecapture')
    modlog.info("Initializing specify")
    specify.datapipeline(rxndict, vardict)

def linkprocess(linkfile):
    pass

def readvars(rxnvarfile):
    '''
    Processes excel (specifically formatted) excel form and converts to dict
    '''
    rxndict={}
    varfile = (rxnvarfile)
    wb = xlrd.open_workbook(varfile)
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        commentval = sheet.cell(i,0).value
        if commentval == '#':
            pass
        else:
            cell_dict_value = sheet.cell(i,3).value
            cell_dict_id = sheet.cell(i,1).value
            cell_dict_type = sheet.cell(i,4).value
            if cell_dict_id == "":
                pass
            if cell_dict_type == 'list':
                rxndict[cell_dict_id] = ast.literal_eval(cell_dict_value)
            else:
                rxndict[cell_dict_id.strip()] = cell_dict_value
    return(rxndict)

'''
Gather variables input into the XLS form, developer code, and CLI
'''
if __name__ == "__main__":
    vardict={}

    parser = ap.ArgumentParser(description='Generate experimental run data')
    parser.add_argument('Variables', type=str,
        help='Target xls file containing run information specified by the user\
             format should be "filename.xlsx"') 
    parser.add_argument('-s', '--ss', default=0, type=int, choices=[0,1,2], 
        help='0 - quasi-random experiments generate, 1 - Generates stateset\
             for exp_1 user specified reagents, 2 - generate prototype run for\
             exp_1 user specified reagents') 
    parser.add_argument('-d', '--debug', default=0, type=int, choices=[0,1],
        help='0 - complete run generation and upload to google drive,\
             1 - local debugging with no data upload,') 
#    parser.add_argument('-i', '--id', type=str,
#        help='User is able to specify a runID for the generated run')
#    parser.add_argument('-e', '--escalation', type=str,
#        help="User specifies challenge problem crank number for run generation")

    args = parser.parse_args()
    challengeproblem = args.ss
    debug = args.debug

    vardict['exefilename'] = args.Variables
    vardict['max_robot_reagents'] = devconfig.max_robot_reagents
    vardict['RoboVersion'] = devconfig.RoboVersion
    vardict['challengeproblem'] = challengeproblem
    vardict['debug'] = debug
    vardict['volspacing'] = devconfig.volspacing
    vardict['maxreagentchemicals'] = devconfig.maxreagentchemicals
    vardict['solventlist'] = devconfig.solventlist
    vardict['targetfolder'] = devconfig.targetfolder
    vardict['chemsheetid'] = devconfig.chemsheetid
    vardict['chem_workbook_index'] = devconfig.chem_workbook_index
    vardict['reagent_workbook_index'] = int(devconfig.reagent_workbook_index)
    vardict['reagentsheetid'] = devconfig.reagentsheetid

    rxndict = readvars(vardict['exefilename'])
    rxndict['challengeproblem'] = challengeproblem

    #if args.escalation == None:
    #    pass
    #else:
    #    linkfile = str(args.escalation) + '.link.csv'

    if not os.path.exists('localfiles'):
        os.mkdir('localfiles')
    rxndict, vardict = init.runuidgen(rxndict, vardict) 
    loggerfile=init.buildlogger(rxndict)
    rxndict['logfile']=loggerfile
    init.initialize(rxndict, vardict) #logs all variables

    # >>>  Should insert variable tests here <<<<  #

    escalatecapture(rxndict,vardict)