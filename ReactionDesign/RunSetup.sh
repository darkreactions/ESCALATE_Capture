#!/bin/bash


##########################################################
#  _        ___           _                              #
# |_)    o   |   _. ._   |_) _  ._   _| |  _ _|_  _  ._  #
# |_) \/ o  _|_ (_| | |  |  (/_ | | (_| | (/_ |_ (_) | | #
#     /                                                  #
##########################################################
##########################################################
###############################
### Notes on running script ###
###############################
### Link to amine list: https://goo.gl/UZSCBj ############
### Using 'Chemical Abbreviations' are essential for autofill!!! 
### 1) Fillout or verify each variable 
###   a) Stock Solution Information 
###   b) Operational Sequence (Hardcoded Sequence)
### 2) Select preferences for run (coming soon! TM)
### 3) Execute Script 
### 4) Ensure desired setup: https://goo.gl/f2LQDu
### 4) Ensure desired (Debug) setup: https://goo.gl/Sxq5Wd
##########################################################

ExpWrkVer=1.1 #The workflow version of the experimental protocol
Lab=LBL #Options are "LBL" or "HC" (Haverford College)

#########################
### Debugging Options ###
#########################
Db=1 #Debugging 0 turns off debugging, REAL RUNS WIH 0
Pt=0 #Turns on plot display 

############################
### Tray/Robot Variables ###
############################
#All of the following variables set the conditions of the tray, 
SRPM=750 #[range 0-750] v1.1=750, Tray shake rate 
S1Dur=900 #[range > 0]  v1.1=900, Duration of shake after addition of first three reagents
S2Dur=1200 #[range > 0] v1.1=1200, Duration of shake after addition of reagent 5 (formic acid in 1.1)
Temp2=105 #[range 0-90, 105] v1.1=105, Temperature to set the robot, 105 means max temperature = 92 Celsius, 
FinalHold=12600 #[range > 0] v1.1=12600, Duration of reaction after all reagents and shaking protocols are complete.  Holds at Temp2
Wellcount=20 #Total number of wells to run on each tray
molarmin1=0.15 #[range < (ConcStock*MaximumStock)] Lower bound for the mmol of PbI2 in each well ##lower if you get "Box constraints improperly specified: should be [lb, ub] pairs"
maxEquivAmine=4.0 #[range >= SAper] Maximum equiv of amine compared with PbI2, cannot be less than the amount in stockA

################################
### Stock Solution Variables ###
################################
Amine1=EtNH3I #Ensure: https://goo.gl/UZSCBj present, Reagent 2 amine
RTemp=45 #[range 0-105] v1.1=45, Temperature of reagents on the robot deck
DeadVol=2.0 #[range > 0] v1.1=2.0, Dead volume, Volume intentionally left in the bottom of robot reagent trays

## Reagent 2 (StockA) Properties ##
ConcStock=1.5 #[range > 0] v1.1 refers to PbI2 stockA (reagent 2) Molar (M) Concentration 
SAper=1.0 #[range > 0] v1.1 refers to percent amine in StockA (Reagent 2) 2=200% , 0.5=50%
R2PreTemp=75 #Temperature of the reagent while mixing
R2StirRPM=450 #Stir rate of reagent while mixing
R2Dur=3600  #Duration of reagent mixing

## Reagent 3 (StockB) Properties ##
CSAm=6.0 #[range > 0] v1.1 refers to Molar (M) Concentration of Amine 2 in StockB (reagent 3) 
R3PreTemp=75 #Temperature of the reagent while mixing
R3StirRPM=450 #Stir rate of reagent while mixing
R3Dur=3600 #Duration of reagent mixing

## Reagent 5-6 (FAH) Properties ##
molarminFA=0.10 #[range >=0], v1.1=2.0, Minimum mmol of formic acid (sum reagent 5 and 6)
molarmaxFA=5.0 #[range < molarminFA], v1.1=5.0, Maximum mmol of FAH (sum reagent 5 and 6) ##Lower if you get high volume errors

###################################
### Well/Experimental Variables ###
###################################
MaximumStock=500 #[range > 0] v1.1=500, Maximum volume of reagents 1-4 (Should not be adjusted unless absolutely certain)
MaximumWell=700  #[range > MaximumStock] v1.1=700, Total maximum volume permitted in any well after all reagents added

##########################
### Optional Variables ###
##########################
#molarmax1=0.5 #[range >molarmin1] v1.1=default (this option was not set), Manually set the upper bound for mmol of PbI2 in each well.  Default is 100% stockA, limited by the concentration of stock solution A
Temp1=80 #[range >0], v1.1=80, Robot temperature prior to adding any reagents to the wells
Amine2=$Amine1 #v1.1: Amine2=Amine1, #Ensure: https://goo.gl/UZSCBj present, Reagent 3 amine

##################################
### Future Development Options ###
##################################
#These are options which could/should be available in future instances of this program
#Bead = 0 #### 0 is no, 1 is yes
#BeadSize = 4  ### Currently a range from maximum of 6mm to minimum of 2mm (soda lime bead)
############################
### Nasty Execution Line ###
############################
python PythonFiles/RoboJSONScript.py $Db $Pt $Temp1 $SRPM $S1Dur $S2Dur $Temp2 $FinalHold $Amine1 $Amine2 $ConcStock $CSAm $SAper $RTemp $DeadVol $MaximumStock $MaximumWell $maxEquivAmine $Wellcount $molarmin1 $molarminFA $molarmaxFA $R2PreTemp $R2StirRPM $R2Dur $R3PreTemp $R3StirRPM $R3Dur $ExpWrkVer $Lab --molarmax1 $molarmax1