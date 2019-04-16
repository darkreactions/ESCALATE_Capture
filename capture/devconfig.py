# devconfig.py

#version control
RoboVersion = 2.2

# Hard coded limits
max_robot_reagents = 7
maxreagentchemicals = 3
volspacing = 10 #reagent microliter (uL) spacing between points in the stateset 


# perovskite solvent list (simple specification of what is a liquid)
# assumes only 1 liquid / reagent
solventlist = ['GBL', 'DMSO', 'DMF', 'FAH'] #ya, I know FAH isn't a solvent, but it makes programming easier

# Gdrive target folder for rendering
targetfolder = '11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe' #target folder for run generation
chemsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
chem_workbook_index = 0
reagentsheetid = "1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg"
reagent_workbook_index = 1


