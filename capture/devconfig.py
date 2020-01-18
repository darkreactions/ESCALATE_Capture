import platform
import os
import sys

cwd = os.getcwd()


#######################################
# version control
RoboVersion = 2.57
ReportVersion = 0.81 


#######################################
# General Functions (Report and Capture)
SUPPORTED_LABS = ['LBL', 'LBL_WF3_Iodides', 'HC', 'MIT_PVLab', 'ECL']

#######################################
# ESCALATE_Capture settings

maxreagentchemicals = 4
volspacing = 50  # reagent microliter (uL) spacing between points in the stateset

# perovskite solvent list (simple specification of what is a liquid)
# assumes only 1 liquid / reagent
#TODO: read these values from the chemical inventory!
solventlist = ['GBL', 'DMSO', 'DMF', 'DCM', 'CBz']

# Lab-specific variables
lab_vars = {
    'HC':
        {
            'template_folder': '131G45eK7o9ZiDb4a2yV7l2E1WVQrz16d',
            'targetfolder': '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe',
            'chemsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'chem_workbook_index': 0,
            'reagentsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 17,
            'max_reagents': 9,
            'reagent_alias': 'Reagent',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': ['xrd', 'images', 'cytation_image'],
            'observation_interface': {'uid_col': 'E',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
        },
    'LBL':
        {
            'template_folder': '131G45eK7o9ZiDb4a2yV7l2E1WVQrz16d',
            'targetfolder': '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe',
            'chemsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'chem_workbook_index': 0,
            'reagentsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 17,
            'max_reagents': 9,
            'reagent_alias': 'Reagent',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': ['xrd', 'images','cytation_image'],
            'observation_interface': {'uid_col': 'E',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
        },
    'dev':
        {
            'template_folder': '1w5tReXSRvC6cm_rQy74-10QLIlG7Eee0',
            'targetfolder': '19nt2-9Inub8IEYDxOLnplCPDEYt1NPqZ',
            'chemsheetid': '1uj6A3TH2oMSQwzhPapfmr1t-CbevEGmQjKIyfg9aSgk',
            'chem_workbook_index': 0,
            'reagentsheetid': '1uj6A3TH2oMSQwzhPapfmr1t-CbevEGmQjKIyfg9aSgk',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 17,
            'reagent_alias': 'Reagent',
            'max_reagents': 9,
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': ['cytation_image'],
            'observation_interface': {'uid_col': 'B',
                                      'modeluid_col': 'J',
                                      'participantuid_col': 'K'}
        },
    'MIT_PVLab':
        {
            'template_folder': '1PVeVpNjnXiAuzm3Oq2q-RiiLBhKPGW53',
            'targetfolder': '1tUb4GcF_tDanMjvQuPa6vj0n9RNa5IDI',
            'chemsheetid': '1htERouQUD7WR2oD-8a3KhcBpadl0kWmbipG0EFDnpcI',
            'chem_workbook_index': 0,
            'reagentsheetid': '1htERouQUD7WR2oD-8a3KhcBpadl0kWmbipG0EFDnpcI',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 17,
            'max_reagents': 9,
            'reagent_alias': 'Precursor',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': [],
            'observation_interface': {'uid_col': 'B',
                                      'modeluid_col': 'H',
                                      'participantuid_col': 'I'}
        },
}

#######################################
# Wolfram Kernel Management

wolfram_kernel_path = None # ensure the value can be imported on all computers.

system = platform.system()
if system == "Linux":
    wolfram_kernel_path = None
    from pathlib import Path
    # try first path location
    wolfram_kernel = Path('/usr/local/Wolfram/WolframEngine/12.0/Executables/WolframKernel')
    if wolfram_kernel.is_file():
        wolfram_kernel_path = "/usr/local/Wolfram/WolframEngine/12.0/Executables/WolframKernel"
    # try second path location
    wolfram_kernel_2 = Path('/usr/local/Wolfram/Mathematica/12.0/Executables/WolframKernel')
    if wolfram_kernel_2.is_file():
        wolfram_kernel_path = '/usr/local/Wolfram/Mathematica/12.0/Executables/WolframKernel'
    if wolfram_kernel_path is None:
        print('WolframKernel not successfully found, please correct devconfig')
        import sys
        sys.exit()

# Mac or Windows
elif system == "Darwin" or system == 'Windows':
    wolfram_kernel_path = None

# Other
else:
    raise OSError("Your system is likely not supported if it's not Linux, MAC, or Windows")

######################################
# Sampler Selection


# 'wolfram' is currently experimental and unsupported
# must be 'default' or 'wolfram'
sampler = 'wolfram'


######################################
# ESCALATE_report settings

valid_input_files = {
    'preparation_interface': ['ExpDataEntry.json'],  # reagent prep
    'experiment_specification': ['ExperimentSpecification.xls', 'RobotInput.xls'],  # volume file
    'observation_interface': ['observation_interface.csv', 'CrystalScoring.csv'],  # results
    'specification_interface': ['Template', 'SpecificationInterface']  # user input file
}
