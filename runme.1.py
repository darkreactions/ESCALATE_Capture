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

# Challenge Problem Toggle
cp=0                                  #Setting this value to "1" indicates the challenge problem workflow

# Plotting options
ploton=0                              #Setting this value to "1" turns on plotting on


##############################
### Experiment Information ###
##############################
lab = 'LBL'                           #Options are "LBL" or "HC" (Haverford College)
reagentcount = 7                      # How many reagents are present in the current reaction
wellcount = 96                        # (maximum 96) Total number of experimental wells on the plate 
reagent_combination1 = [1,2,3,6,7]    # combination of reagents added to a particular experiment - presented as a list 
#reagent_combination2 = [1,4,5,6,7]   # second combination of reagents added to a separate set of experiments on the same plate - presented as a list 
reagent_target_volume = 4000           #[range > 0] v1.1=500, Maximum volume of reagents 1-4 (Should not be adjusted unless absolutely certain)
maximum_total_volume = 4500            #[range > MaximumStock] v1.1=700, Total maximum volume permitted in any well after all reagents added


############################
###   Plate Conditions   ###
############################
#All of the followidg variables set the conditions of the tray,
#Examples discussed in the context of perovskite workflow 1
stirrate = 750                        #[range 0-750] v1.1=750, Tray shake rate in rpm (only a single value for now)
temperature1_nominal = 80             #[range >0], v1.1=80, temperature robot will reach prior to adding any reagents to the wells
duratation_stir1 = 900                #[range > 0]  v1.1=900, Duration of shake after addition of first three reagents 
duratation_stir2 = 1200               #[range > 0] v1.1=1200, Duration of shake after addition of reagent 5 and 6 (formic acid in 1.1)
temperature2_nominal = 105            #[range 25-120, 105] v1.1=105, Temperature to set the robot for the ITC process
temperature2_actual = 92              #[range 0-90, 105] v1.1=105, Temperature the ITC process is anticipated to reach during the course of reaaction 
duration_reaction = 12600             #[range > 0] v1.1=12600, Duration of ITC after all reagents and shaking protocols are complete.  Holds at temperature 2
reagent_dead_volume = 3.0             #[range > 0] v1.1=3.0, Dead volume, excess reagent prepared, ensures that enough solution will be present for plate
plate_container = 'Symyx_96_well_0003'

############################
### Chemical Information ###
############################

#chemical 1 (GBL)
chem1_abbreviation = 'GBL'            # Abbreviation from chemical list https://goo.gl/UZSCBj    

#chemical 2 (PbI2)
chem2_abbreviation = 'PbI2'           # Abbreviation from chemical list https://goo.gl/UZSCBj    
chem2_min = 0.15                       # [range < (ConcStock*MaximumStock)] Lower bound for the mmol of PbI2 in each well ##lower if you get "Box constraints improperly specified: should be [lb, ub] pairs"
chem2_max=7.24                       #Manually set the upper bound for mmol of PbI2 in each well.  Default is 100% stockA, limited by the concentration of stock solution A

#chemical 3 (Amine1)
chem3_abbreviation = 'FormamidiniumIodide'         # Abbreviation from chemical list https://goo.gl/UZSCBj  #Ensure: https://goo.gl/UZSCBj present, Reagent 2 amine
#chem3_min = 0.0
#chem3_max = 10.0
max_equiv_chem3_to_chem2 = 4.0        #[range >= reag2_target_conc_chemical2] Maximum equiv of amine (chemical 3) compared with PbI2 (chemical 2), cannot be less than the percentage of amine in reagent 2

#chemical 4 (Amine2)
#chem4_abbreviation = 'n-BuNH3I'       # Abbreviation from chemical list https://goo.gl/UZSCBj    
#max_equiv_chem4_to_chem2 = 6.0        #[range >= reag2_target_conc_chemical2] Maximum equiv of amine (chemical 3) compared with PbI2 (chemical 2), cannot be less than the percentage of amine in reagent 2

#chemical 5 (Formic Acid)
chem5_abbreviation = 'FAH'            # Abbreviation from chemical list https://goo.gl/UZSCBj    
chem5_molarmin = 0.1                  # [range < (ConcStock*MaximumStock)] Lower bound for the mmol of PbI2 in each well ##lower if you get "Box constraints improperly specified: should be [lb, ub] pairs"
chem5_molarmax = 5.0                  # [range < (ConcStock*MaximumStock)] Lower bound for the mmol of PbI2 in each well ##lower if you get "Box constraints improperly specified: should be [lb, ub] pairs"

############################
###  Reagent Information ###
############################
###  REAGENT Defaults  ###            # If no specific value is set for a reagent these will be used (if only one chemical only reagents_prerxn_temperature will be used)
reagents_prerxn_temperature = 45      # [range 0-105] v1.1=45, units (C) Temperature of reagents immediately prior to addition to experiment / well 
reagents_prep_temperature = 75        # Temperature of reagent during preparation (C) 
reagents_prep_stirrate = 450          # Stir rate during prepration (rpm)
reagents_prep_duration = 3600         # Stir duration (s)

#Reagent 1 information
reag1_chemicals = [1]                 # List of the chemicals present in reagent 1, in order of addition

#Reagent 2 information
reag2_chemicals = [1,2,3]             # List of the chemicals present in reagent 2, in order of addition
reag2_target_conc_chemical2 = 1.81     # PbI2 target molarity [M] [range > 0] v1.1) in the final solution (not accounting for non-idea solvent behavior)
reag2_target_conc_chemical3 = 1.36     # Amine 1  target molarity [M]
#reag2_prep_temperature = 75           # Temperature of reagent during preparation (C) 
#reag2_prep_stirrate = 450             # Stir rate during prepration (rpm)
#reag2_prep_duration = 3600            # Stir duration (s)

#Reagent 3 information
reag3_chemical_makeup = [1,3]         # List of the chemicals present in reagent 3, in order of addition
reag3_target_conc_chemical2 = 2.63     # Amine 1  target molarity [M]
#reag3_prep_temperature = 75           # Temperature of reagent during preparation (C) 
#reag3_prep_stirrate = 450             # Stir rate during prepration (rpm)
#reag3_prep_duration = 3600            # Stir duration (s)

#Reagent 4 information
#reag4_chemical_makeup = [1,2,4]       # List of the chemicals present in reagent 4, in order of addition
#reag4_target_conc_chemical2 = 1.5     # PbI2 target molarity [M] [range > 0] v1.1) in the final solution (not accounting for non-idea solvent behavior)
#reag4_target_conc_chemical4 = 3.0     # Amine 1  target molarity [M]
#reag4_prep_temperature = 75           # Temperature of reagent during preparation (C) 
#reag4_prep_stirrate = 450             # Stir rate during prepration (rpm)
#reag4_prep_duration = 3600            # Stir duration (s)

#Reagent 5 information
#reag5_chemical_makeup = [1,4]         # List of the chemicals present in reagent 5, in order of addition
#reag5_target_conc_chemical4 = 6.0     # Amine 1  target molarity [M]
#reag5_prep_temperature = 75           # Temperature of reagent during preparation (C) 
#reag5_prep_stirrate = 450             # Stir rate during prepration (rpm)
#reag5_prep_duration = 3600            # Stir duration (s)

#Reagent 6 information
reag6_chemical_makeup = [5]           # List of the chemicals present in reagent 6, in order of addition

#Reagent 7 information
reag7_chemical_makeup = [5]           # List of the chemicals present in reagent 6, in order of addition

######################################################################################################################################################################
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
    rxndict['RoboVersion']=2.0 #Workflow version of the robotic JSON generation script (this script)
    loggerfile=logger.buildlogger(rxndict)
    rxndict['logfile']=loggerfile
    rxndict=logger.cleanvalues(rxndict)
    expgenerator.initialize(rxndict)