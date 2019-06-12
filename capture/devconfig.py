# devconfig.py

import platform

#######################################

#version control
RoboVersion = 2.4

# Hard coded limits
max_robot_reagents = 7
maxreagentchemicals = 3
volspacing = 100 #reagent microliter (uL) spacing between points in the stateset

#######################################

# perovskite solvent list (simple specification of what is a liquid)
# assumes only 1 liquid / reagent
solventlist = ['GBL', 'DMSO', 'DMF', 'DCM']

# lab file requirements list

#######################################

# Gdrive target folder for rendering
targetfolder = '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe' #target folder for run generation
chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
chem_workbook_index = 0
reagentsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
reagent_workbook_index = 1
reagent_interface_amount_startrow = 15

#######################################

system = platform.system()

if system == "Linux":
    wolfram_kernel_path = '/usr/local/Wolfram/Mathematica/12.0/Executables/WolframKernel'
# Mac
elif system == "Darwin":
    wolfram_kernel_path = None

#######################################

def labfiles(lab):
    if lab == "LBL" or lab == "HC":
        filereq = ['CrystalScoring','ExpDataEntry','metadata.json']
    if lab == 'ECL':
        filereq = ['CrystalScoring','metadata.json']
    return(filereq)

######################################
# Sampler

# must be 'default' or 'wolfram'
# 'wolfram' is currently experimental and unsupported
sampler = 'wolfram'
