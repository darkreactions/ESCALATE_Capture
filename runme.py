import os
import sys
import argparse as ap
import ast
from script import expgenerator
from log import logger
import xlrd

## Development flags
max_robot_reagents = 7
RoboVersion = 2.1

def linkprocess(linkfile):
    pass

def readvars(rxnvarfile):
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


if __name__ == "__main__":
    vardict={}
    rxnvarfile = "WF1_variables.xlsx"

    parser = ap.ArgumentParser(description='Generate experimental run data')
    parser.add_argument('--cp', default=0, type=int, choices=[0,1], 
        help='1 - Generates state set for challenge problem, 0 - default \
            run generation') 
    parser.add_argument('-d', '--debug', default=0, type=int, choices=[0,1],
        help='1 - local debugging with no data upload, 0 - complete run\
            generation and upload to google drive') 
    parser.add_argument('-i', '--id', type=str,
        help='User is able to specify a runID for the generated run')
    parser.add_argument('-e', '--escalation', type=str,
        help="User specifies challenge problem crank number for run generation")

    # Challenge Problem / escalation Toggle
    args = parser.parse_args()
    challengeproblem = args.cp
    debug = args.debug
    vardict['exefilename'] = rxnvarfile
    vardict['max_robot_reagents'] = max_robot_reagents

    if args.escalation == None:
        pass
    else:
        linkfile = str(args.escalation) + '.link.csv'

    rxndict = readvars(rxnvarfile)
    vardict['debug'] = debug
    vardict['challengeproblem'] = challengeproblem
    rxndict['challengeproblem'] = challengeproblem
    if not os.path.exists('localfiles'):
        os.mkdir('localfiles')
    rxndict, vardict = logger.runuidgen(rxndict, vardict) 
    loggerfile=logger.buildlogger(rxndict, vardict)
    rxndict['logfile']=loggerfile
    logger.initialize(rxndict)
    expgenerator.datapipeline(rxndict, vardict)