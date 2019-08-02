import platform

#######################################
# version control
RoboVersion = 2.5

SUPPORTED_LABS = ['LBL', 'HC', 'MIT_PVLab', 'ECL', 'dev']

#######################################
# chemistry-relevant specifications

maxreagentchemicals = 4
volspacing = 50  # reagent microliter (uL) spacing between points in the stateset

#######################################
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
            'reagent_interface_amount_startrow': 15,
            'max_reagents': 7,
            'reagent_alias': 'Reagent',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': ['xrd', 'images'],
            'observation_interface': {'uid_col': 'E'}
        },
    'LBL':
        {
            'template_folder': '131G45eK7o9ZiDb4a2yV7l2E1WVQrz16d',
            'targetfolder': '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe',
            'chemsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'chem_workbook_index': 0,
            'reagentsheetid': '1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 15,
            'max_reagents': 7,
            'reagent_alias': 'Reagent',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': ['xrd', 'images'],
            'observation_interface': {'uid_col': 'E'}
        },
    'dev':
        {
            'template_folder': '1w5tReXSRvC6cm_rQy74-10QLIlG7Eee0',
            'targetfolder': '19nt2-9Inub8IEYDxOLnplCPDEYt1NPqZ',
            'chemsheetid': '1uj6A3TH2oMSQwzhPapfmr1t-CbevEGmQjKIyfg9aSgk',
            'chem_workbook_index': 0,
            'reagentsheetid': '1uj6A3TH2oMSQwzhPapfmr1t-CbevEGmQjKIyfg9aSgk',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 16,
            'reagent_alias': 'Reagent',
            'max_reagents': 8,
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': [],
            'observation_interface': {'uid_col': 'F'}
        },
    'MIT_PVLab':
        {
            'template_folder': '1PVeVpNjnXiAuzm3Oq2q-RiiLBhKPGW53',
            'targetfolder': '1tUb4GcF_tDanMjvQuPa6vj0n9RNa5IDI',
            'chemsheetid': '1htERouQUD7WR2oD-8a3KhcBpadl0kWmbipG0EFDnpcI',
            'chem_workbook_index': 0,
            'reagentsheetid': '1htERouQUD7WR2oD-8a3KhcBpadl0kWmbipG0EFDnpcI',
            'reagent_workbook_index': 1,
            'reagent_interface_amount_startrow': 16,
            'max_reagents': 8,
            'reagent_alias': 'Precursor',
            'required_files': ['observation_interface', 'preparation_interface', 'metadata.json'],
            'required_folders': [],
            'observation_interface': {'uid_col': 'F'}
        },
}

#######################################
# Wolfram Kernel Management


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
# Mac
elif system == "Darwin":
    wolfram_kernel_path = None

######################################
# Sampler Selection


# must be 'default' or 'wolfram'
# 'wolfram' is currently experimental and unsupported
sampler = 'default'
