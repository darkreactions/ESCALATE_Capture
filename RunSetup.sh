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
Debugging=1   

######################
### Stock Solution ###
######################

A1="EtNH3I"
A2="EtNH3I"
#A3=""
VS=18.0 #total intended volume of stock solution
##WV=500 #total volume in each well

######################
### Environmental  ###
######################
#Bead = 0 #### 0 is no, 1 is yes
#BeadSize = 4  ### Currently a range from maximum of 6mm to minimum of 2mm (soda lime bead)

############################
### Operational Sequence ###
############################

Temp1=80      #First Temperature Setting - Celcius ## 105 is actually 95
Temp2=105     #Second Temperature Setting - Celcius ## 105 is actually 95
#Dispense reagents 1-5
S_RPM=500     #All Shake RPM #Robot limitation
S1_Time=900   #First Shake Duration - Seconds
#Dispense reagent 6
S2_Time=1200  #Second Shake Duration - Seconds
FH=9000       #Final Hold Duration - Seconds

############################
python RoboJSONScript.py $A1 $A2 $VS $Temp1 $S_RPM $S1_Time $S2_Time $Temp2 $FH $Debugging
