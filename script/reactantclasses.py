#Building the reaction classes for containing the relevant variables
#designed specifically for use with workflow 2.0 of the code generator
#Idea with the reagent class is to ensure that the values calculated for a single reagent remain together with the reagent object
class perovskitereagent:
    # attributes all of the properties of the reagent to a single object
    def __init__(self, reactantinfo, rxndict, entry, chemdf):
        self.name = entry # reag1, reag2, etc
        self.chemicals = reactantinfo['chemicals'] # list of the chemicals in this reagent
        self.concs = self.concentrations(reactantinfo, chemdf, rxndict) # unpack the concentration information

        #passes the reaction preparation step if a pure chemical (this is a stop gap until autoprotocol intergration)
        if len(self.chemicals) > 1:
            self.preptemperature = self.preptemp(reactantinfo, rxndict)
            self.prepstirrate = self.prepstir(reactantinfo, rxndict)
            self.prepduration = self.prepdur(reactantinfo, rxndict)
        else:
            self.preptemperature = "null"
            self.prepstirrate = "null"
            self.prepduration = "null"
        self.preptempunits = "celsius"
        self.prepstirunits = "rpm"
        self.prepdurunits = "seconds"

    #checks for user specified values, if none, returns default 
    def preptemp(self, reactantinfo, rxndict):
        try:
            self.preptemperature = reactantinfo['prep_temperature']
        except:
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
                if [key for key,value in reactantinfo.items() if variablename in key] == []:
                        #density / molecular weight function returns mol / L of the chemical
                        concdict[updatedname] = (float(chemdf.loc[rxndict['chem%s_abbreviation'%chemical],"Density            (g/mL)"])/ chemdf.loc[rxndict['chem%s_abbreviation' %chemical],"Molecular Weight (g/mol)"] * 1000)
            else: pass
        return(concdict)

class perovskitechemical:
    def __init__(self, rxndict, chemdf):
        pass
