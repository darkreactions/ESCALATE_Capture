import logging
import pandas as pd

import gspread
from capture.googleapi import googleio
from oauth2client.service_account import ServiceAccountCredentials

from utils.data_handling import get_used_reagent_nums

def build_reagentdf(reagsheetid, reagsheetworkbook):
    """Read the reagents workbook from Google Drive and return a pandas DataFrame

    :param reagsheetid:        TODO this is a workbook (and unused)
    :param reagsheetworkbook:  TODO this is a sheet    (Rest in a Pendletonian manner)
    :return reagdf: pandas DF representation of the reagent worksheet
    """

    # Setup google drive connection
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc = gspread.authorize(credentials)
    reagsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"

    # open sheet, or book? todo notice the inconsistencies in nomenclature here
    ReagentBook = gc.open_by_key(reagsheetid)
    reagentsheet = ReagentBook.get_worksheet(reagsheetworkbook)
    reagent_list = reagentsheet.get_all_values()

    # Parse sheet to df
    reagdf = pd.DataFrame(reagent_list, columns=reagent_list[0])
    reagdf = reagdf.iloc[1:]
    reagdf = reagdf.reset_index(drop=True)
    reagdf = reagdf.set_index('ECL_Model_ID')
    return reagdf


def buildreagents(rxndict, chemdf, reagentdf, solventlist):
    """Return rdict, a mapping from reagent IDs to perovskitereagent objects

    Checks that reagents were only specified in one manner in the Template: 'list-style' or with a ModelID
    """
    modlog = logging.getLogger('capture.models.reagent.buildreagents')
    reagentdict = {}


    used_reagent_nums = get_used_reagent_nums(rxndict)
    for item in rxndict:

        # parse 'list-style' reagent specifications from Template
        if 'Reagent' in item and "chemical_list" in item:
            reagentname = item.split('_')[0]
            ## ensure that the reagent definition is not being defined in two different ways
            idflag = reagentname + "_ID"
            if idflag in rxndict:
                print('too many %s' % reagentname)
            else:
                entry_num = reagentname.split('t')[1]
                reagentvariables = {}
                reagentvariables['reagent'] = reagentname

                if int(entry_num) not in used_reagent_nums:
                    continue

                for variable, value in rxndict.items():
                    if reagentname in variable and '(ul)' not in variable:
                        variable = variable.split('_', 1)
                        reagentvariables[variable[1]] = value

                reagent = perovskitereagent(reagentvariables,
                                            rxndict,
                                            entry_num,
                                            chemdf,
                                            solventlist)

                reagentdict[entry_num] = reagent

        #parse specifications from reagent model ID
        elif "Reagent" in item and "_ID" in item:
            reagentvariables = {}
            reagentname = item.split('_')[0]
            entry_num = reagentname.split('t')[1]
            if int(entry_num) not in used_reagent_nums:
                continue
            reagentid = rxndict[item]
            reagentvariables['reagent'] = reagentname
            chemical_list = []

            for columnheader in reagentdf.columns:
                if "item" and "abbreviation" in columnheader:
                    chemicalname = (reagentdf.loc["%s" %reagentid, columnheader])
                    if chemicalname == 'null':
                        pass
                    else:
                        chemical_list.append(chemicalname)

                reagentvariables[columnheader] = reagentdf.loc["%s" %reagentid, columnheader]

            reagentvariables['chemical_list'] = chemical_list

            reagent = perovskitereagent(reagentvariables,
                                        rxndict,
                                        entry_num,
                                        chemdf,
                                        solventlist)

            reagentdict[entry_num] = reagent

    for k,v in reagentdict.items():
        modlog.info("%s : %s" %(k,vars(v)))

    return reagentdict


class perovskitereagent:
    """Reaction class containing user specified and calculated variables

    numerically order reagents specified by the user are associated with calculated values
    attributes all of the properties of the reagent should be contained within this object
    """
    def __init__(self, reactantinfo, rxndict, reagentnumber, chemdf, solvent_list):
        self.name = reagentnumber # reag1, reag2, etc
        self.chemicals = reactantinfo['chemical_list'] # list of the chemicals in this reagent

        # {item<i>_formulaconc: concentration for all chemical item indices i in self}
        self.concs = self.concentrations(reactantinfo, chemdf, rxndict)
        self.ispurebool = self.ispure()
        self.solventnum = self.solvent(solvent_list)  # todo bad name is bad, this should be solventindex  
        self.solvent_list = solvent_list

        #passes the reaction preparation step if a pure chemical 
        if len(self.chemicals) > 1:
            self.preptemperature = self.preptemp(reactantinfo, rxndict)
            self.prepstirrate = self.prepstir(reactantinfo, rxndict)
            self.prepduration = self.prepdur(reactantinfo, rxndict)
        else:
            self.preptemperature = "null"
            self.prepstirrate = "null"
            self.prepduration = "null"
        self.prerxntemp = self.prerxn(reactantinfo, rxndict)
        self.preptempunits = "celsius"
        self.prepstirunits = "rpm"
        self.prepdurunits = "seconds"

    @property
    def component_dict(self):
        """
        :return: a dict mapping: chemical_names => concentrations
        """
        out = {}
        for item_i, conc in self.concs.items():
            i = int(item_i[-1]) - 1  # zero index the chemical names
            chemical_name = self.chemicals[i]
            if chemical_name not in self.solvent_list:
                out[chemical_name] = conc

        return out

    #checks for user specified values, if none, returns default
    def prerxn(self, reactantinfo, rxndict):
        try:
            self.prerxntemp = reactantinfo['prerxn_temperature']
        except Exception:
            self.prerxntemp = rxndict['reagents_prerxn_temperature']
        return(self.prerxntemp)

    def preptemp(self, reactantinfo, rxndict):
        try:
            self.preptemperature = reactantinfo['prep_temperature']
        except Exception:
            self.preptemperature = rxndict['reagents_prep_temperature']
        return(self.preptemperature)

    #checks for user specified values, if none, returns default 
    def prepstir(self, reactantinfo, rxndict):
        try:
            self.prepstirrate = reactantinfo['prep_stirrate']
        except:
            self.prepstirrate = rxndict['reagents_prep_stirrate']
        return(self.prepstirrate)

    def prepdur(self, reactantinfo, rxndict):
        try:
            self.prepduration = reactantinfo['prep_duration']
        except:
            self.prepduration = rxndict['reagents_prep_duration']
        return(self.prepduration)
    
    def solvent(self, solventlist):
        if len(self.chemicals) > 1:
            ## automated solvent detection could go here
            solventnum = self.chemicals[-1:][0]
        else: 
            solventnum = 0
        return(solventnum)

    def ispure(self):
        modlog = logging.getLogger('capture.perovskitereagent.ispure')
        if len(self.chemicals) == 1:
            return(1)
        elif len(self.chemicals) > 1:
            return(0)
        else:
            modlog.Error("Reagents are improperly constructed!")

    def concentrations(self, reactantinfo, chemdf, rxndict):
        """Return a dict mapping {item<i>_formulaconc: concentration for all chemical item indices i in self}
        :param reactantinfo:
        :param chemdf:
        :param rxndict:
        :return:
        """
        concdict = {}
        chemicalitem = 1
        for chemical in self.chemicals:
            # todo talk to ian about this:
            # this name seems like it doesnt ever exist in the spreadsheet
            # and so the listcomp below will always evaluate to the empty list
            variablename = 'item%s_formulaconc' %chemical
            updatedname = 'conc_chem%s' %chemical
#            for key, value in reactantinfo.items():
#                if 'chemical' in key:
#                    if variablename in key:
#                        concdict[updatedname] = value
#                print(concdict)
            if len(self.chemicals) == 1:
                itemlabel = 'conc_item1' 
                if [key for key in reactantinfo.keys() if variablename in key] == []:
                        #density / molecular weight function returns mol / L of the chemical
                        try:
                            concdict[itemlabel] = (float(chemdf.loc[self.chemicals[0],"Density            (g/mL)"])/ \
                                                   float(chemdf.loc[self.chemicals[0],"Molecular Weight (g/mol)"]) * 1000)
                        except:
                            pass
            else:
                try:
                    itemlabel = 'conc_item%s' %chemicalitem 
                    itemname = 'item%s_formulaconc' %chemicalitem
                    if reactantinfo[itemname] == 'null':
                        pass
                    else:
                        concdict[itemlabel] = float(reactantinfo[itemname])
                    chemicalitem+=1
                except Exception:
                    pass
        return(concdict)
