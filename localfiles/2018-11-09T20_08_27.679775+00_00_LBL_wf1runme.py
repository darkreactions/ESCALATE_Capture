#Copyright (c) 2018 Ian Pendleton - MIT License
########################################################################################
###                            Summary of running script                             ###
########################################################################################
### Link to chemical list: https://goo.gl/UZSCBj                                     ###
### Using 'Chemical Abbreviations' are essential for autofill!                       ### 
########################################################################################
###                    Please be sure to read the README.md file!                    ###
########################################################################################
### 1) Fillout or verify each variable                                               ###
###   a) Update reagent information                                                  ###
###   b) Update reagent preparation (default or individually)                        ###
###   c) Update desired chemical constraints on the nominal concentrations           ###
### 2) Ensure the experiment and portions are correctly identified                   ###
### 3)After adjusting to the desired variables execute the python script by running: ###
### -->   python3 wf1runme.py  (or this files current name)                          ###
### 4) Ensure desired experiment is setup appropriately:  https://goo.gl/Sxq5Wad     ###
########################################################################################

ExpWorkflowVer=1.1                    #The workflow version of the experimental protocol

# Show plot for each experiment before submitting?
plotter_on = 0                        # 1 = on , 0 = off (default)

#################################
### Tray / Plate  Information ###
#################################
lab = 'LBL'                           # Options are "LBL" or "HC" (Haverford College), or ECL (pending dev)
wellcount = 96                       # (#)    [range <96] Total number of experimental wells to run on the plate 
exp1 = [[2,3,1],[5,6]]                # [[portion1_reagent1, portion1_reagent2], [portion2_reagent#]] Last reagent will be used to fill. First reagent will be targeted for maximum search range available. 
exp1_vols = [[500,500],[0,250]]       # [[portion1_minimum_vol, portion1_max_vol], [portion2_min_vol,portion2_max_vol]] Volume min and max allocated to each portion of a single experiment 

############################
###   Plate Conditions   ###
############################
#All of the following variables set the conditions of the plate
#Examples for WF1
stirrate = 750                         # (rmp) [range 0-750] v1.1=750, Plate shake rate in rpm (only a single value for now)
temperature1_nominal = 80              # (C)   [range >0], v1.1=80, temperature robot will reach prior to adding any reagents to the wells
duratation_stir1 = 900                 # (s)   [range > 0]  v1.1=900, Duration of shake after addition of first three reagents 
duratation_stir2 = 1200                # (s)   [range > 0] v1.1=1200, Duration of shake after addition of reagent 5 and 6 (formic acid in 1.1)
temperature2_nominal = 105             # (C)   [range 25-120, 105] v1.1=105(programmed), 92(actual), ITC process robot temp
duration_reaction = 12600              # (s)   [range > 0] v1.1=12600, Duration of ITC after all reagents and shaking protocols are complete.  Holds at temperature 2
reagent_dead_volume = 3.0              # (mL)  [range > 0] v1.1=3.0, Dead volume, excess reagent prepared, ensures that enough solution will be present for plate
plate_container = 'Symyx_96_well_0003' # Plate identifier (manual, no checks on this entry)

############################
### Chemical Information ###
############################

#chemical 1 (GBL)
chem1_abbreviation = 'GBL'             # Abbreviation from chemical list https://goo.gl/UZSCBj    

#chemical 2 (PbI2)
chem2_abbreviation = 'PbI2'            # Abbreviation from chemical list https://goo.gl/UZSCBj    
#chem2_molarmin = 0.2                  # Lower [M] molar concentration for chemical2 in any given portion for all experiments
#chem2_molarmax = 1.5                  # Upper [M] molar concentration for chemical2 in any given portion for all experiments

#chemical 3 (Amine1)
chem3_abbreviation = 'iButylammoniumIodide'        # Abbreviation from chemical list https://goo.gl/UZSCBj  #Ensure: https://goo.gl/UZSCBj present, Reagent 2 amine
#chem3_molarmin = 3.0                  # Lower [M] molar concentration for chemical3 in any given portion for all experiments 
#chem3_molarmax = 4.0                  # Upper [M] molar concentration for chemical3 in any given portion for all experiments 

#chemical 5 (Formic Acid)
chem5_abbreviation = 'FAH'             # Abbreviation from chemical list https://goo.gl/UZSCBj    
#chem5_molarmin = 0.0                  # Lower [M] molar concentration for chemical3 in any given portion for all experiments 
#chem5_molarmax = 5.5                  # Upper [M] molar concentration for chemical3 in any given portion for all experiments 

############################
###  Reagent Information ###
############################
###  REAGENT Defaults  ###             # Default values will be used for all reagents without specifications
reagents_prerxn_temperature = 45       # [range 0-105] v1.1=45, units (C) Temperature of reagents immediately prior to addition to experiment / well 
reagents_prep_temperature = 75         # Temperature of reagent during preparation (C) 
reagents_prep_stirrate = 450           # Stir rate during prepration (rpm)
reagents_prep_duration = 3600          # Stir duration (s)

#Reagent 1 information
reag1_chemicals = [1]                  # List of the chemicals present in reagent 1, in order of addition

#Reagent 2 information
reag2_chemicals = [2,3,1]              # List of the chemicals present in reagent 2, user should provide in PRIORITY order
reag2_target_conc_chemical2 = 2.40     # PbI2 stock concentration target molarity [M] [range > 0] v1.1) in the final solution (not accounting for non-idea solvent behavior)
reag2_target_conc_chemical3 = 3.00     # Amine 1  target molarity [M]
#reag2_prep_temperature = 75           # Overrides reagent default preparation temperature (C)       ## To use on other reagents change reag# number
#reag2_prep_stirrate = 450             # Overrides reagent default preparation stir rate (rpm)       ## To use on other reagents change reag# number
#reag2_prep_duration = 3600            # Overrides reagent default stir duration (s)                 ## To use on other reagents change reag# number

#Reagent 3 information
reag3_chemicals = [3,1]                # List of the chemicals present in reagent 3, in order of addition
reag3_target_conc_chemical3 = 12.6     # Amine 1  target molarity [M]
#reag3_prep_temperature = 75           # Overrides reagent default preparation temperature (C)       ## To use on other reagents change reag# number
#reag3_prep_stirrate = 450             # Overrides reagent default preparation stir rate (rpm)       ## To use on other reagents change reag# number
#reag3_prep_duration = 3600            # Overrides reagent default stir duration (s)                 ## To use on other reagents change reag# number

#Reagent 5 information
reag5_chemicals = [5]                  # List of the chemicals present in reagent 6, in order of addition
reag5_prerxn_temperature = 22          # [range 0-105] v1.1=45, units (C) Temperature of reagents immediately prior to addition to experiment / well 

#Reagent 6 information
reag6_chemicals = [5]                  # List of the chemicals present in reagent 6, in order of addition
reag6_prerxn_temperature = 22          # [range 0-105] v1.1=45, units (C) Temperature of reagents immediately prior to addition to experiment / well 

######################################################################################################################################################################
######################################################################################################################################################################
import argparse as ap
parser = ap.ArgumentParser(description='Generate experimental run data')
parser.add_argument('--cp', default=0, type=int, help='Activates the challenge problem pipeline. Default = 0 (standard pipeline)') #Default, debugging on and real code off == "1"
parser.add_argument('-d', '--debug', default=0, type=int, help='Disables dataupload. Default = 0 (Upload enabled)') #Default, debugging on and real code off == "1"

max_robot_reagents = 7
RoboVersion = 2.0

# Challenge Problem Toggle
args = parser.parse_args()
challengeproblem = args.cp
debug = args.debug
######################################################################################################################################################################
######################################################################################################################################################################
if __name__ == "__main__":
    localsdictionaryholder = {}
    import os
    import sys
    exefilename = sys.argv[0]
    if not os.path.exists('localfiles'):
        os.mkdir('localfiles')
    for x,y in locals().copy().items():
        if "__" in x or "localsdictionaryholder" in x:
            pass
        else:
            localsdictionaryholder[x]=y
    from script import expgenerator
    from script import logger
    rxndict=logger.runuidgen(localsdictionaryholder) 
    loggerfile=logger.buildlogger(rxndict)
    rxndict['logfile']=loggerfile
#    rxndict=logger.cleanvalues(rxndict)
    logger.initialize(rxndict)
    expgenerator.datapipeline(rxndict)
    #####################################
    ### Old outdated but new sampling ###
    #####################################
    # Use this as a fallback - only <insert higher conciousness here> knows what it does
#    expgenerator.CreateRobotXLS(rxndict)