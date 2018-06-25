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

######################
### Environmental  ###
######################
#Bead = 0 #### 0 is no, 1 is yes
#BeadSize = 4  ### Currently a range from maximum of 6mm to minimum of 2mm (soda lime bead)

############################
python RoboJSONScript.py $Debugging
