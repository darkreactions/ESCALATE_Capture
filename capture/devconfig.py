import platform
import os
import sys
from pathlib import Path

cwd = os.getcwd()
#######################################
# Version Control
RoboVersion = 2.60
######################################
# Sampler Selection
sampler = 'wolfram' # options are 'default' or 'wolfram'
# 'wolfram' is default, if wolfram fails, fall back to default using this toggle
######################################
# ESCALATE_Capture settings
volspacing = 50  # reagent microliter (uL) spacing between points in the stateset generation
'''
  Targets for lab specific will overrides (defaults used otherwise)
target folder MUST be set for a lab, no default will be provided
new labs should be added to the specification interfaces after testing
'''
lab_vars = {
    'default':
        {
            ## Template Handling START ##
            'template_folder': '131G45eK7o9ZiDb4a2yV7l2E1WVQrz16d',
            'maxreagentchemicals' : 4,
            'max_reagents': 9,
            'reagent_interface_amount_startrow': 17,
            ## Template Handling END ##
            ## Inventory START ##
            'chemsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'chem_workbook_index': 0,
            'reagentsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'reagent_workbook_index': 1,
            ## Inventory END ##
            ## Semantic Start ##
            'reagent_alias': 'Reagent',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': ['experiment_characterizations'],
            'observation_interface': {'uid_col': 'E',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
            ## Semantic END ##
        },
    'HC':
        {
            ## LAB START ##
            'newrun_remote_folder': '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe',
            ## LAB END ##
            ## Semantic START ##
            'required_folders': ['xrd', 'images', 'cytation_image'],
            'observation_interface': {'uid_col': 'E',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
            ## Semantic END ##
        },
    'LBL':
        {
            'newrun_remote_folder': '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe',
            'required_folders': ['xrd', 'images','cytation_image'],
            'observation_interface': {'uid_col': 'E',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
        },
    'ECL':
        {
            'newrun_remote_folder': '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe',
            'required_folders': ['images'],
            'observation_interface': {'uid_col': 'E',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
        },
    'dev':
        {
            'newrun_remote_folder': '19nt2-9Inub8IEYDxOLnplCPDEYt1NPqZ',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'observation_interface': {'uid_col': 'B',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
        },
    'MIT_PVLab':
        {
            'template_folder': '1PVeVpNjnXiAuzm3Oq2q-RiiLBhKPGW53',
            'newrun_remote_folder': '1tUb4GcF_tDanMjvQuPa6vj0n9RNa5IDI',
            'chemsheetid': '1hputxEjnjaERKaBC5FjUqsYGewAtyVsUzH-bBImF6yE',
            'chem_workbook_index': 0,
            'reagentsheetid': '1hputxEjnjaERKaBC5FjUqsYGewAtyVsUzH-bBImF6yE',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 17,
            'max_reagents': 9,
            'reagent_alias': 'Precursor',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': [],
            'observation_interface': {'uid_col': 'B',
                                      'modeluid_col': 'I',
                                      'participantuid_col': 'J'}
        },
}

#######################################
# ESCALATE_report settings
# Naming variations in the main escalate data tracking files
valid_input_files = {
    'preparation_interface': ['ExpDataEntry.json'],  # reagent prep
    'experiment_specification': ['ExperimentSpecification.xls', 'RobotInput.xls'],  # volume file
    'observation_interface': ['observation_interface.csv', 'CrystalScoring.csv'],  # results
    'specification_interface': ['Template', 'SpecificationInterface']  # user input file
}

''' specified targets for data workup, 
    Add new google drive folders here the target data folder must be structured correctly,
this isn't magic just plumbing. An example of the correct structure can be found here:
https://drive.google.com/open?id=1rPNGq69KR7_8Zhr4aPEV6yLtB6V4vx7k

'''
#TODO: assign desired calculations to each dataset, add a safe/generalizable default 
# .   The dict of desired calculations should only toggle on options, not specify
# .   The default should not include 'target_data_folder", these should always be assigned
workup_targets = {
    '4-Data-Bromides':
        {
            'target_data_folder' : '147uGb_15iwpqb082KOYBE2xyT9djEmKv',
        },
    '4-Data-Iodides':
        {
            'target_data_folder' : '13xmOpwh-uCiSeJn8pSktzMlr7BaPDo7B',
        },
    '4-Data-WF3_Iodide':
        {
            'target_data_folder' : '11CcFTLw7mu4tnnv8QO1opSE7XQiEP32L',
        },
    '4-Data-WF3_Alloying':
        {
            'target_data_folder' : '12hOt8BVeQgsFWVa6gM56kNBMF3NJUi0I',
        },
    'dev':
        {
            'target_data_folder' : '1rPNGq69KR7_8Zhr4aPEV6yLtB6V4vx7k',
        },
    'MIT_PVLab':
        { 
            'target_data_folder' : '1VNsWClt-ppg8ojUztDYssnSgfoe9XRhi',
        }
}

#######################################
######### KERNAL MANAGEMENT ###########
#######################################

### WOLFRAM KERNEL MANAGEMENT ###
# first check that system is supported: do one thing at a time
system = platform.system()
if system not in ['Linux', 'Darwin', 'Windows']:
    # Dont kill, just warn. If it dies, it dies. If it doesn't: cool!
    print("Warning: OS not officially supported") 


wolfram_kernel_path = None # ensure the value can be imported on all computers.

# we only need to do this check if the user wants wolfram in the first place
linux_path = '/usr/local/Wolfram/WolframEngine/12.1/Executables/WolframKernel'
if sampler == 'wolfram': 
    if system == "Linux":
        wolfram_kernel_path = None
        # try first path location
        wolfram_kernel = Path(linux_path)
        if wolfram_kernel.is_file():
            wolfram_kernel_path = linux_path
        # try second path location
        wolfram_kernel_2 = Path(linux_path)
        if wolfram_kernel_2.is_file():
            wolfram_kernel_path = linux_path
        if wolfram_kernel_path is None:
            # is this allowed? maybe can do in a cleaner way but nice to automate this instead of just killing
            print('Warning: WolframKernel not successfully found, falling back on default')
            sampler = 'default' 
# Mac or Windows
elif system == "Darwin" or system == 'Windows':
    wolfram_kernel_path = None
### END WOLFRAM ###

### CHEMDESCRIPTOR KERNALS ### 
# These should point to the JChemSuite/bin!
CXCALC_PATH = '/Applications/JChemSuite/bin/'

CALC_POSSIBLE = False
STANDARDIZE_POSSIBLE = False

cxcalc_path = Path(CXCALC_PATH)
if cxcalc_path.joinpath('cxcalc').is_file():
    CALC_POSSIBLE = True
if cxcalc_path.joinpath('standardize').is_file():
    STANDARDIZE_POSSIBLE = True

os.environ['CXCALC_PATH'] = CXCALC_PATH
os.environ['STANDARDIZE_PATH'] = CXCALC_PATH

### END CHEMDESCRIPTOR ###