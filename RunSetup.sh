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
##########################################################

######################
### Stock Solution ###
######################

A1="EtNH3I"
A2="n-BuNH3I"
A3="PhEtNH3I"
VS=18.0 #total intended volume of stock solution

############################
### Operational Sequence ###
############################
Temp1=22      #First Temperature Setting - Celcius
#Dispense reagents 1-5
S_RPM=900    #All Shake RPM #Robot limitation
S1_Time=900   #First Shake Duration - Seconds
#Dispense reagent 6
S2_Time=1200  #Second Shake Duration - Seconds
Temp2=90      #Second Temperature Setting - Celcius
FH=9000       #Final Hold Duration - Seconds

############################
python RoboJSONScript.py $A1 $A2 $A3 $VS $Temp1 $S_RPM $S1_Time $S2_Time $Temp2 $FH
