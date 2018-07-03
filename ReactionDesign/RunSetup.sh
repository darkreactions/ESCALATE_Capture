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

##  Debugging 0 turns off debugging, REAL RUNS WIH 0
Db=1
Pt=1 #Turns on plot display 

######################
### Stock Solutio ###
######################
#All of the following variables set the conditions of the tray
SRPM=750
S1Dur=900
S2Dur=1200
Temp2=105
FinalHold=12600
Amine1=n-BuNH3I
Amine2=n-BuNH3I
ConcStock=1.5
CSAm=5
SAper=1.0
RTemp=45
DeadVol=2.0
MaximumStock=500
MaximumWell=700 
maxEquivAmine=2.2
Wellcount=96
molarmin1=0.40
molarminFA=2.0
molarmaxFA=5.0

######################
### Stock Solution ###
######################

R2PreTemp=75
R2StirRPM=450
R2Dur=3600
R3PreTemp=75
R3StirRPM=450
R3Dur=3600

######################
### Environmental  ###
######################
#Bead = 0 #### 0 is no, 1 is yes
#BeadSize = 4  ### Currently a range from maximum of 6mm to minimum of 2mm (soda lime bead)
Temp1=80
############################
python PythonFiles/RoboJSONScript.py $Db $Pt $Temp1 $SRPM $S1Dur $S2Dur $Temp2 $FinalHold $Amine1 $Amine2 $ConcStock $CSAm $SAper $RTemp $DeadVol $MaximumStock $MaximumWell $maxEquivAmine $Wellcount $molarmin1 $molarminFA $molarmaxFA $R2PreTemp $R2StirRPM $R2Dur $R3PreTemp $R3StirRPM $R3Dur
