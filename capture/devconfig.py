import platform

#######################################
# version control todo: ian where does this get used? Not sure if we should have to manually do this
RoboVersion = 2.5


#######################################
# chemistry-relevant specifications

max_robot_reagents = 7
maxreagentchemicals = 3
volspacing = 5  # reagent microliter (uL) spacing between points in the stateset

# perovskite solvent list (simple specification of what is a liquid)
# assumes only 1 liquid / reagent
solventlist = ['GBL', 'DMSO', 'DMF', 'DCM']

#######################################
# Gdrive information

template_folder = '1PVeVpNjnXiAuzm3Oq2q-RiiLBhKPGW53'
targetfolder = '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe'  # target folder for new experiments
chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
chem_workbook_index = 0
reagentsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
reagent_workbook_index = 1
reagent_interface_amount_startrow = 15

#######################################
# Wolfram Kernel Management

system = platform.system()
if system == "Linux":
    wolfram_kernel_path = '/usr/local/Wolfram/\
                           Mathematica/12.0/Executables/WolframKernel'
# Mac
elif system == "Darwin":
    wolfram_kernel_path = None

######################################
# Sampler Selection

# must be 'default' or 'wolfram'
# 'wolfram' is currently experimental and unsupported
sampler = 'wolfram'

#######################################
# Laboratory file management

def labfiles(lab):
    """Returns files that need to be sent to a given laboratory"""
    if lab == "LBL" or lab == "HC":
        filereq = ['CrystalScoring', 'ExpDataEntry', 'metadata.json']
    if lab == 'ECL':
        filereq = ['CrystalScoring', 'metadata.json']
    return filereq
