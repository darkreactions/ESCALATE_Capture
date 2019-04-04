import logging


def buildreagents(rxndict, chemdf, solventlist):
    modlog = logging.getLogger('capture.models.reagent.buildreagents')
    ''' builds dictionary of reagents based on user specifications of formulas and chemicals 

    parses initial user input and generates a dictionary of reagents with relevant properties
    '''
    reagentlist=[]
    reagentdict={}
    #find all of the reagents constructured in the run
    for item in rxndict:
        if 'Reagent' in item and "chemical_list" in item:
            reagentname=(item.split('_'))
            reagentlist.append(reagentname[0])
    #Turn all of those reagents into class objects
    for entry in reagentlist:
        reagentvariables={}
        reagentvariables['reagent']=entry
        entry_num = entry.split('t')
        for variable,value in rxndict.items(): 
            if entry in variable:
                variable=(variable.split('_',1))
                reagentvariables[variable[1]]=value
        reagent=perovskitereagent(reagentvariables, rxndict, entry_num[1], chemdf, solventlist)  # should scale nicely, class can be augmented without breaking the code
        #return the class objects in a new dictionary for later use!
        reagentdict[entry_num[1]]=reagent
    for k,v in reagentdict.items(): 
        modlog.info("%s : %s" %(k,vars(v)))
    return(reagentdict)


class perovskitereagent:
    ''' Reaction class containing user specified and calculated variables 

    numerically order reagents specified by the user are associated with calculated values 
    attributes all of the properties of the reagent should be contained within this object
    '''
    def __init__(self, reactantinfo, rxndict, entry, chemdf, solventlist):
        self.name = entry # reag1, reag2, etc
        self.chemicals = reactantinfo['chemical_list'] # list of the chemicals in this reagent
        self.concs = self.concentrations(reactantinfo, chemdf, rxndict) 
        self.ispurebool = self.ispure()
        self.solventnum = self.solvent(solventlist)

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
        concdict = {}
        for chemical in self.chemicals:
            variablename = 'conc_chemical%s' %chemical
            updatedname = 'conc_chem%s' %chemical
            for key, value in reactantinfo.items():
                if 'chemical' in key:
                    if variablename in key:
                        concdict[updatedname] = value
            #Some string that happened to work which only prints key, value pairs of single chemicals as long as they lack a "target_conc" description
            #likely brittle
            if len(self.chemicals) == 1:
                itemlabel = 'conc_item1' 
                if [key for key,value in reactantinfo.items() if variablename in key] == []:
                        #density / molecular weight function returns mol / L of the chemical
                        concdict[itemlabel] = (float(chemdf.loc[rxndict['chem%s_abbreviation'%chemical],"Density            (g/mL)"])/ \
                            float(chemdf.loc[rxndict['chem%s_abbreviation' %chemical],"Molecular Weight (g/mol)"]) * 1000)
            else:
                try:
                    itemlabel = 'conc_item%s' %chemical 
                    itemname = 'item%s_formulaconc' %chemical
                    concdict[itemlabel] = reactantinfo[itemname]
                except Exception:
                    pass
        return(concdict)
    
