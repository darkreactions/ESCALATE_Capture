#Copyright (c) 2018 Ian Pendleton - MIT License
########################################################################################
###                            Summary of running script                             ###
########################################################################################
### Link to chemical list: https://goo.gl/UZSCBj                                        ###
### Using 'Chemical Abbreviations' are essential for autofill!                       ### 
########################################################################################
###                    Please be sure to read the README.md file!                    ###
########################################################################################
### 1) Fillout or verify each variable                                               ###
###   a) Stock Solution Information                                                  ###
###   b) Operational Sequence (Hardcoded Sequence)                                   ###
### 2) Select preferences for run (coming soon! TM)                                  ###
### 3)After adjusting to the desired variables execute the python script by running: ###
### -->   python3 runsetup.py                                                        ###
### 4) Ensure desired experiment is setup appropriately:  https://goo.gl/Sxq5Wad     ###
########################################################################################

ExpWorkflowVer=1.1                    #The workflow version of the experimental protocol
# Show plot for each experiment before submitting?
plotter_on = 0                              # 1 = on , 0 = off (default)

#################################
### Tray / Plate  Information ###
#################################
#First reagent 
lab = 'LBL'                           #Options are "LBL" or "HC" (Haverford College)
wellcount = 96                        # (maximum 96) Total number of experimental wells on the plate 
exp1 = [[2,3,1],[5,6]]                # combination of reagents added to a particular experiment. First reagent is always 'solvent', second reagent will be targeted for maximum search range available. 
exp1_vols = [[500,500],[0,250]]                # Volume allocated to each list in the the exp.  For instance [500,250] would mean a total final volume of 750uL
#exp1_wells = 20                       # number of experimental wells to dedicate to a particular experiment
#exp2 = [[4,5,1],[6,7]]
#exp2_vols = [[3000,3000],[1000,1000]]
#exp2_wells = 40
#exp3 = [[2,1]]
#exp3_vols = [[100,100]]
#exp3_wells = 36
reagent_target_volume = 500           #[range > 0] v1.1=500, Maximum volume of reagents 1-4 (Should not be adjusted unless absolutely certain)
maximum_total_volume = 750            #[range > MaximumStock] v1.1=700, Total maximum volume permitted in any well after all reagents added

############################
###   Plate Conditions   ###
############################
#All of the following variables set the conditions of the tray,
#Examples discussed in the context of perovskite workflow 1
stirrate = 750                        #[range 0-750] v1.1=750, Tray shake rate in rpm (only a single value for now)
temperature1_nominal = 80             #[range >0], v1.1=80, temperature robot will reach prior to adding any reagents to the wells
duratation_stir1 = 900                #[range > 0]  v1.1=900, Duration of shake after addition of first three reagents 
duratation_stir2 = 1200               #[range > 0] v1.1=1200, Duration of shake after addition of reagent 5 and 6 (formic acid in 1.1)
temperature2_nominal = 105             #[range 25-120, 105] v1.1=105, Temperature to set the robot for the ITC process
duration_reaction = 12600             #[range > 0] v1.1=12600, Duration of ITC after all reagents and shaking protocols are complete.  Holds at temperature 2
reagent_dead_volume = 3.0             #[range > 0] v1.1=3.0, Dead volume, excess reagent prepared, ensures that enough solution will be present for plate
plate_container = 'Symyx_96_well_0003'

############################
### Chemical Information ###
############################

#chemical 1 (GBL)
chem1_abbreviation = 'GBL'             # Abbreviation from chemical list https://goo.gl/UZSCBj    

#chemical 2 (PbI2)
chem2_abbreviation = 'PbI2'            # Abbreviation from chemical list https://goo.gl/UZSCBj    
chem2_molarmin = 0.2                  # Lower [M] molar concentration for chemical2 in any given portion for all experiments
#chem2_molarmax = 1.5                  # Upper [M] molar concentration for chemical2 in any given portion for all experiments

#chemical 3 (Amine1)
chem3_abbreviation = 'PhEtNH3I'          # Abbreviation from chemical list https://goo.gl/UZSCBj  #Ensure: https://goo.gl/UZSCBj present, Reagent 2 amine
#chem3_molarmin = 3.0                  # Lower [M] molar concentration for chemical3 in any given portion for all experiments 
#chem3_molarmax = 4.0                  # Upper [M] molar concentration for chemical3 in any given portion for all experiments 

#chemical 4 (Amine2)
#chem4_abbreviation = 'n-BuNH3I'        # Abbreviation from chemical list https://goo.gl/UZSCBj    
#chem4_molarmin = 0.0                  # Lower [M] molar concentration for chemical4 in any given portion for all experiments
#chem4_molarmax = 1.0                  # Upper [M] molar concentration for chemical4 in any given portion for all experiments 

#chemical 5 (Formic Acid)
chem5_abbreviation = 'FAH'             # Abbreviation from chemical list https://goo.gl/UZSCBj    
#chem5_molarmin = 0.0                  # Lower [M] molar concentration for chemical3 in any given portion for all experiments 
#chem5_molarmax = 5.5                  # Upper [M] molar concentration for chemical3 in any given portion for all experiments 

############################
###  Reagent Information ###
############################
###  REAGENT Defaults  ###             # If no specific value is set for a reagent these will be used (if only one chemical only reagents_prerxn_temperature will be used)
reagents_prerxn_temperature = 45       # [range 0-105] v1.1=45, units (C) Temperature of reagents immediately prior to addition to experiment / well 
reagents_prep_temperature = 75         # Temperature of reagent during preparation (C) 
reagents_prep_stirrate = 450           # Stir rate during prepration (rpm)
reagents_prep_duration = 3600          # Stir duration (s)

#Reagent 1 information
reag1_chemicals = [1]                  # List of the chemicals present in reagent 1, in order of addition

#Reagent 2 information
reag2_chemicals = [2,3,1]              # List of the chemicals present in reagent 2,  in order of priority for constraints
reag2_target_conc_chemical2 = 2.22     # PbI2 target molarity [M] [range > 0] v1.1) in the final solution (not accounting for non-idea solvent behavior)
reag2_target_conc_chemical3 = 1.11     # Amine 1  target molarity [M]
        #Example Manual Overrides
#reag2_prep_temperature = 75           # Overrides reagent default preparation temperature  ## To use on other reagents just change the respective reagent number
#reag2_prep_stirrate = 450             # Overrides reagent default Stir rate during prepration (rpm) ## To use on other reagents just change the respective reagent number
#reag2_prep_duration = 3600            # Overrides reagent default Stir duration (s)## To use on other reagents just change the respective reagent number

#Reagent 3 information
reag3_chemicals = [3,1]                # List of the chemicals present in reagent 3, in order of addition
reag3_target_conc_chemical3 = 1.57     # Amine 1  target molarity [M]

#Reagent 4 information
#reag4_chemicals = [2,4,1]             # List of the chemicals present in reagent 4, in order of addition
#reag4_target_conc_chemical2 = 2.0     # PbI2 target molarity [M] [range > 0] v1.1) in the final solution (not accounting for non-idea solvent behavior)
#reag4_target_conc_chemical4 = 1.4     # Amine 1  target molarity [M]

#Reagent 5 information
reag5_chemicals = [5]                  # List of the chemicals present in reagent 6, in order of addition
reag5_prerxn_temperature = 22       # [range 0-105] v1.1=45, units (C) Temperature of reagents immediately prior to addition to experiment / well 
#reag5_chemicals = [4,1]               # List of the chemicals present in reagent 5, in order of addition
#reag5_target_conc_chemical4 = 7.4     # Amine 1  target molarity [M]
        #End of upcoming settings

#Reagent 6 information
reag6_chemicals = [5]                   # List of the chemicals present in reagent 6, in order of addition
reag6_prerxn_temperature = 22       # [range 0-105] v1.1=45, units (C) Temperature of reagents immediately prior to addition to experiment / well 

#Reagent 7 information
#reag7_chemicals = [5]                  # List of the chemicals present in reagent 6, in order of addition

######################################################################################################################################################################
######################################################################################################################################################################
import argparse as ap
parser = ap.ArgumentParser(description='Generate experimental run data')
parser.add_argument('--cp', default=0, type=int, help='Activates the challenge problem pipeline. Default = 0 (standard pipeline)') #Default, debugging on and real code off == "1"
parser.add_argument('--debug', default=0, type=int, help='Disables dataupload. Default = 0 (Upload enabled)') #Default, debugging on and real code off == "1"

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