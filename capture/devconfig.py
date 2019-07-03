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
solventlist = ['GBL', 'DMSO', 'DMF', 'DCM', 'chlorobenzene']

#######################################
# Gdrive information

# Gdrive target folder for rendering
#MIT
#template_folder = '1PVeVpNjnXiAuzm3Oq2q-RiiLBhKPGW53'
#targetfolder = '1tUb4GcF_tDanMjvQuPa6vj0n9RNa5IDI' #  target folder for run generation
#chemsheetid = "1htERouQUD7WR2oD-8a3KhcBpadl0kWmbipG0EFDnpcI"
#chem_workbook_index = 0
#reagentsheetid = "1htERouQUD7WR2oD-8a3KhcBpadl0kWmbipG0EFDnpcI"
#reagent_workbook_index = 1
#reagent_interface_amount_startrow = 15

#HC LBL
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

#######################################
# Laboratory file management

def labfiles(lab):
    """Returns files that need to be sent to a given laboratory"""
    if lab == "LBL" or lab == "HC":
        filereq = ['CrystalScoring', 'ExpDataEntry', 'metadata.json']
    if lab == 'ECL':
        filereq = ['CrystalScoring', 'metadata.json']
    return filereq
