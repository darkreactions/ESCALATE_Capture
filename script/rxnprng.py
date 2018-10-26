import optunity
import pandas as pd
import numpy as np
from script import plotter
import logging
import sys
from script import testing

modlog = logging.getLogger('initialize.rxnprng')
                    
##Place holder function.  This can be fit to change the distribution of points at a later time. For now
## the method returns only the sobol value unmodified.  The sampling in each input x1, x2, x3 should be evenly distributed
## and unaltered.  (Blank function)
def f(x1):
    return 0.0

def reagentdataframe(volmax, volmin, reagent, wellnum):
    _, info_random, _ = optunity.minimize(f, num_evals=wellnum, x1=[volmin, volmax], solver_name='sobol')
    print(volmax,volmin)
    ##Create quasi-random data spread
    reagentlist=info_random.call_log['args']['x1'] #Create reagent amounts (mmol), change x variable to change range, each generated from unique sobol index
    reagentname = "Reagent%s" %reagent
    rdf = pd.DataFrame({reagentname:reagentlist}).astype(int)
    return(rdf)
    #Generate a range of Amine concentrations dependent upon the range possible due to the presence of amine in Stock solution A \


def calcvollimit(userlimits, reagent, rdata, volmax, volmin): 
    chemicals = rdata.chemicals
    possiblemaxvolumes = []
    possiblemaxvolumes.append(volmax)
    possibleminvolumes = []
    possibleminvolumes.append(volmin)
    # Determine if any user constraints override the maximum concentrations dependent on the volume limits
    for chemical in chemicals:
        #The code will update the maximum volume to meet the lower bound requirements set by the user
        try: 
            maxconc = (rdata.concs['conc_chem%s' %chemical])
            userdefinedmax = (userlimits['chem%s_molarmax'%chemical])
            if userdefinedmax < maxconc:
                volmaxnew = userdefinedmax / maxconc * volmax
                possiblemaxvolumes.append(int(volmaxnew))
            else: modlog.warning("User defined concentration greater than physically possible for chemical%s" %chemical)
        except Exception:
            pass
        #The code will update the minimum volume to meet the lower bound requirements set by the user
        try: 
            reagconc = (rdata.concs['conc_chem%s' %chemical])
            userdefinedmin = (userlimits['chem%s_molarmin'%chemical])
            if userdefinedmin > 0:
                volminnew = userdefinedmin / reagconc * volmax
                possibleminvolumes.append(int(volminnew))
            else: pass
        except Exception:
            pass
    if (min(possiblemaxvolumes)) != volmax:
        modlog.warning("User has constrained the maximum search space by lowering the maximum value for a chemical in reagent %s, be sure this is intentional" % reagent)
        volmax = min(possiblemaxvolumes)
    if (max(possibleminvolumes)) != 0:
        modlog.warning("User has constrained the maximum search space by raising the minimum value for a chemical in reagent %s, be sure this is intentional" % reagent)
        volmin = max(possibleminvolumes)
    else: pass
    testing.reagenttesting(volmax,volmin)
    return(volmax, volmin)


def portiondataframe(expoverview, rdict, vollimits, rxndict, wellnum, userlimits):
#    print(len(vollimits), (reagents))
    portionnum = 0 
    for portion in expoverview:
        # need the volume minimum and maximum and well count 
        reagentcount = 0
        reagenttotal = len(portion)
        # Determine from the chemicals and the remaining volume the maximum and minimum volume possible for the sobol method
        volmax = vollimits[portionnum][1]
        rdf = pd.DataFrame()
        for reagent in portion:
            volmin = vollimits[portionnum][0]
            # Unique set of requirements for the first entry
            if reagentcount == 0:
                volmin = 0 # for the first of a set of reagents the minimum volume that can be added is always presumed to be 0
                volmax, volmin = calcvollimit(userlimits, reagent, rdict['%s'%reagent], volmax, volmin)
                rdfnew = reagentdataframe(volmax, volmin, reagent, wellnum)
                reagentcount+=1
                pass
            #operate within the available ranges taken from the previous constraints
            if reagentcount < reagenttotal:
#                volmax, volmin = calcvollimit(userlimits, reagent, rdict['%s'%reagent], volmax, volmin)
            
                pass
            if reagentcount == reagenttotal:
                #Make sure that the portion is filled using the final reagent! 
                pass
            rdf.append(rdfnew, ignore_index=True)
            reagentcount+=1
        # Do things using the adjusted ranges (taking information from the previous runs to adjust remaining volumes...)
#                modlog.info("Reagent min and max were constrained by %s" %(chemical))
#                modlog.info('Minimum and maximum volumes for reagent%s, %s and %s respectively' %(reagent, reagmin, reagmax))
        portionnum+=1
        # Use the reagent min and max along with the well count to generate the preliminary dataframe for this particular reagent in this portion of the experiment on this tray
    
    # Concatenate the reagent volumes for each portion of the experiment.






def preprocess(chemdf, rxndict, edict, rdict, climits):
    experiment = 1
    modlog.info('Making a total of %s unique experiments on the tray' %rxndict['totalexperiments'])
    while experiment < rxndict['totalexperiments']+1:
        modlog.info('Initializing dataframe construction for experiment %s' %experiment)
        experimentname = 'exp%s' %experiment
        count=0
        for k,v in edict.items():
            if experimentname in k:
                if 'wells' in k:
                    wellnum = int(v)
                if 'vols' in k:
                    vollimits=(v)
                else:
                    pass
        modlog.info('Building reagent constraints for experiment %s using reagents %s for a total of %s wells' %(experiment, edict[experimentname], wellnum) )
        portiondataframe(edict[experimentname], rdict, vollimits, rxndict, wellnum, climits)
        # Return the reagent data frame with the volumes for that particular portion of the plate
        modlog.info('Succesfully built experiment %s which returned.... ' %(experiment))
        experiment+=1
    #combine the experiments for the tray into one full set of volumes for all the wells on the plate
    modlog.info('Begin combining the experimental volume dataframes')
    pass


##Function SobolReagent generates the quasi-random distribution of points from the ranges indicated for each variable in the optunity.minimize function.
## The function returns a pandas array consisting of sobol distributed reagent concentrations as well as calculated columns for the other reagents
## The def f function above can be modified to bias the distribution.  See the optunity documentation for more help
def sobolreagent(chemdf, rxndict):
    _, info_random, _ = optunity.minimize(f, num_evals=rxndict['wellcount'], x1=[rxndict['chem2_min'], rxndict['chem2_max']], solver_name='sobol')
#    _, info_FA, _ = optunity.minimize(f2, num_evals=wellcount, x1=[molarminFA, (molarmaxFA/2)], x2=[molarminFA,(molarmaxFA/2)], solver_name='sobol')
    ##Create quasi-random data spread
    Reagentmm2=info_random.call_log['args']['x1'] #Create reagent amounts (mmol), change x variable to change range, each generated from unique sobol index
    Reagentmm3=[]
    #Generate a range of Amine concentrations dependent upon the range possible due to the presence of amine in Stock solution A \
    # The range is set to cover from the minimum physically possible through a X:1 ratio of Amine:PbI2.  Change the (rxndict['chem3_max']/rxndict['chem2_max']) value to something to alter
    for mmolLeadI in Reagentmm2:
        StockAAminePercent=(rxndict['reag2_target_conc_chemical3']/rxndict['reag2_target_conc_chemical2'])
        molarminAmine=float(mmolLeadI)*StockAAminePercent #Set minimum to the physical limit (conc can't be lower than in the stock)
#        print(molarminAmine, rxndict['reag2_target_conc_chemical2']*StockAAminePercent, mmolLeadI*(rxndict['chem3_max']/rxndict['chem2_max'])+mmolLeadI*(rxndict['chem3_max']/rxndict['chem2_max'])*.001 )
        ReagACheck=(mmolLeadI/rxndict['reag2_target_conc_chemical2'])
        if molarminAmine < mmolLeadI*StockAAminePercent: #If value of minimum is set too low, adjust the value to be reasonable
            molarminAmine=rxndict['reag2_target_conc_chemical2']*StockAAminePercent-rxndict['reag2_target_conc_chemical2']*.001*StockAAminePercent #Make sure that the minimum is always a little less (prevents breaking sobol)
            _, info_amine, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*(rxndict['chem3_max']/rxndict['chem2_max'])], solver_name='sobol')
            newMolMinAmine=info_amine.call_log['args']['x1']
            newMolMinAmineUnpack=(newMolMinAmine[0])
            while (ReagACheck+((newMolMinAmineUnpack-mmolLeadI*StockAAminePercent)/rxndict['reag3_target_conc_chemical2'])) > rxndict['reagent_target_volume']/1000:  ## If the draw generates a maximum that would push the total well volume, redefine range and redraw
                _, info_amine2, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*(rxndict['chem3_max']/rxndict['chem2_max'])], solver_name='sobol')
                newMolMinAmine=info_amine2.call_log['args']['x1']
                newMolMinAmineUnpack=(newMolMinAmine[0])
        else:  # if minimum is fine draw from full range
            _, info_amine, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*(rxndict['chem3_max']/rxndict['chem2_max'])+mmolLeadI*(rxndict['chem3_max']/rxndict['chem2_max'])*.001], solver_name='sobol')
            newMolMinAmine=info_amine.call_log['args']['x1']
            newMolMinAmineUnpack=(newMolMinAmine[0])
            count=0
            while (ReagACheck+((newMolMinAmineUnpack-mmolLeadI*StockAAminePercent)/rxndict['reag3_target_conc_chemical3'])) > rxndict['reagent_target_volume']/1000: ## If the draw generates a maximum that would push the total well volume, redefine range and redraw
                _, info_amine2, _ = optunity.minimize(f, num_evals=1, x1=[molarminAmine, mmolLeadI*(rxndict['chem3_max']/rxndict['chem2_max'])], solver_name='sobol')
                newMolMinAmine=info_amine2.call_log['args']['x1']
                newMolMinAmineUnpack=(newMolMinAmine[0])
                if count < 50:  # Sometimes the range between min and max is too tight and sobol doesn't behave well.  This sets the value of the amine stock to the remainder of the well volume
                    if ReagACheck > 0.48:
                        newMolMinAmineUnpack=(.500-ReagACheck)*rxndict['reag3_target_conc_chemical3']+mmolLeadI*StockAAminePercent
                # Should prevent death loop.... but the code hasn't been finished.  For the most part this code shouldn't be needed until UI on DRP is finished
                if count > 50: 
                    print("Amine Ratio Maximum Very High. Strongly Recommend Adjusting")
                    newMolMinAmineUnpack=0
                    print(ReagACheck, newMolMinAmineUnpack)
                    break 
    # print(mmolLeadI, molarminAmine, newMolMinAmineUnpack)
        Reagentmm3.append(newMolMinAmineUnpack) # Append the value for the calculated mmol of amine to the list
    # Create Formic Acid Arrays
    _, info_FA, _ = optunity.minimize(f2, num_evals=rxndict['wellcount'], x1=[rxndict['chem5_molarmin'], (rxndict['chem5_molarmax'])], solver_name='random search')
    Reagentmm5 = info_FA.call_log['args']['x1']
    Reagentmm6=[]
    for mmolFA in Reagentmm5:
        if mmolFA < rxndict['chem5_molarmax']:
            availmmol = rxndict['chem5_molarmax']-mmolFA
            _, info_FA2, _ = optunity.minimize(f2, num_evals=1, x1=[0, availmmol], solver_name='random search')
            Reagentmm6item=info_FA2.call_log['args']['x1']
            Reagentmm6.append(Reagentmm6item[0])
    rmmdf=pd.DataFrame()  #Construct primary data frames r2df=pd.DataFrame()  r2df means reagent 2 dataframe
    rmmdf.insert(0, "mmol %s" %rxndict['chem2_abbreviation'], Reagentmm2)
    rmmdf.insert(1, "mmol %s" %rxndict["chem3_abbreviation"], Reagentmm3)
    rmmdf.insert(0, "mmol 1 %s" %rxndict["chem5_abbreviation"], Reagentmm5)
    rmmdf.insert(0, "mmol 2 %s" %rxndict["chem5_abbreviation"], Reagentmm6)
    return(Reagentmm2, Reagentmm3, Reagentmm5, Reagentmm6, rmmdf)

def ReagentVolumes(chemdf, rxndict):

    # create data frames of target mmol of material
    ReagentmmList=sobolreagent(chemdf, rxndict)
    reagmmol_df = ReagentmmList[4]
    rmmdf=pd.DataFrame()  #Construct primary data frames r2df=pd.DataFrame()  r2df means reagent 2 dataframe
    rmmdf2=pd.DataFrame()  #Construct primary data frames r2df=pd.DataFrame()  r2df means reagent 2 dataframe

    rmmdf.insert(0, "mmol %s" %rxndict['chem2_abbreviation'], ReagentmmList[0])
    rmmdf.insert(1, "mmol %s" %rxndict["chem3_abbreviation"], ReagentmmList[1])
    rmmdf2.insert(0, "mmol 1 %s" %rxndict["chem5_abbreviation"], ReagentmmList[2])
    rmmdf2.insert(0, "mmol 2 %s" %rxndict["chem5_abbreviation"], ReagentmmList[3])
    hold=rmmdf2.iloc[:,0]+rmmdf2.iloc[:,1]
#    plotter.plotme(ReagentmmList[0],ReagentmmList[1], hold.tolist())

    # Convert mmol into the actual amounts of stock solution
    Stock={'Stock A':[rxndict['reag2_target_conc_chemical2'],rxndict['reag2_target_conc_chemical3']],'Stock B':[0,rxndict['reag3_target_conc_chemical3']]} #Stock A is the mixture, B is all amine
    Stockdf=pd.DataFrame(data=Stock)
    rmmdf_trans=rmmdf.transpose()
    rmmdf.insert(2, "FA mmol", ReagentmmList[2])
    rmmdf.insert(3, "FA2 mmol", ReagentmmList[3])
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    with open('localfiles/%s_LogFile.log' %rxndict['RunID'], "a") as f:
        print(rmmdf, file=f)

    # Converting the mmol of the reagents to volumes of the stock solutions in each well
    Stockdf_inverse= pd.DataFrame(np.linalg.pinv(Stockdf.values))
    npVols=np.transpose(np.dot(Stockdf_inverse, rmmdf_trans))  #Unrefined matrix of Volumes of the stock solutions needed for each well in the robotics run

    # Calculating the total volume of formic acid needed for each run 
    rmmdf3=rmmdf2*float(chemdf.loc["FAH","Molecular Weight (g/mol)"]) / float(chemdf.loc["FAH","Density            (g/mL)"])
    rmmdf4=rmmdf3.rename(columns={"FA mmol":"Reagent5 (ul)", "FA2 mmol": "Reagent6 (ul)" })
    npVolsdf=pd.DataFrame({"Reagent2 (ul)": npVols[:,0], "Reagent3 (ul)": npVols[:,1]})*1000

    # Setting up the remaining data frames
    rdf=(pd.concat([npVolsdf,rmmdf4], axis=1)) #Main dataframe containing the total volumes of the reagents for the robot
    r1df=(rxndict['reagent_target_volume']-(rdf.iloc[:,0]+rdf.iloc[:,1])) #Calculates the remaining volume of GBL needed for the reaction r4df=(rdf.iloc[:,0]*0)  #Creates a correctly sized column of zeros
    r4df=(r1df*0)
    rdf.insert(0,'Reagent1 (ul)', r1df)
    rdf.insert(3,'Reagent4 (ul)', r4df)
    return(rdf.round())  ##Returns a pandas dataframe with all of the calculated reagent amounts.
