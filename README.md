**Authors: Ian Pendleton, Michael Tynes, Aaron Dharna**

**Science Contact:** jschrier .at. fordham.edu, ian .at. pendletonian.com

**Technical Debugging:** vshekar .at. haverford.edu, gcattabrig .at. haverford.edu,

**Alternative Debugging:** mtynes .at. fordham.edu, adharna .at. fordham.edu

Overview
=================
A detailed description of the current functionality and logic for this code can be in the [original ESCALATE publication.](https://drive.google.com/open?id=11UfmPuS3e2Y83FtaCJ5VeNanDyprKRR7)

[User documents can be found here.](https://docs.google.com/document/d/1RQJvAlDVIfu19Tea23dLUSymLabGfwJtDnZwANtU05s/edit#)

Installation
=============

This code has been tested on MacOS High Sierra and Ubuntu 18.04 LTS.  Though written in python the code interfaces with
Google API and may require debugging for operation on other operating systems and IDEs.

To build the proper environment using anaconda (https://conda.io/docs/user-guide/install/index.html) do the following:

1. Deactivate any current conda instance: `conda deactivate`

2. Create new python 3.7 environment in conda

      `conda create -n escalate python=3.7`

3. Activate the new environment
      
      `conda activate escalate`

4. Execute the following additional command: 

      `pip install -r requirements.txt`

5. If you need to run the mathematica sampler please install wolfram engine on your operating system.  Follow instructions here: https://www.wolfram.com/engine/

   * Once installed please change the sampler option from 'default' to 'wolfram' in the file capture/devconfig.py
   * Wolfram occasionally updates the engine.  Default is set to detect version 12.1.  If you receive a 'wolfram client' not found error, please check the linux_path in ./capture/devconfig.py 

If during the installation process you encounter any issues, please submit a bug report / issue to https://github.com/darkreactions/ESCALATE_Capture

Installation on Windows:

1. [Download and install anaconda for windows](https://docs.anaconda.com/anaconda/install/windows/)

2. Download and unzip the zip file (or use git clone) of the [ESCALATE capture code](https://github.com/darkreactions/ESCALATE_Capture)

3. Download and [install wolfram engine](https://www.wolfram.com/engine/) --> [and be sure to activate!!!](https://support.wolfram.com/46069)

   * Wolfram occasionally updates the engine.  Default is set to detect version 12.1.  If you receive a 'wolfram client' not found error, please check the linux_path in ./capture/devconfig.py 

4. Open a miniconda window and navigate to the unzipped ESCALATE_Capture-master folder

5. Create new python 3.8 environment in conda.  (This can also be installed in the same environment [as the ESCALATE_report](https://github.com/darkreactions/ESCALATE_report)) 
  
    `conda create -n escalate python=3.8`

6. Activate the new environment 

    `conda activate escalate`

7. Install necessary python packages using pip

     `pip install -r requirements.txt`

### Authentication Setup

1. Download the [securekey files](https://www.youtube.com/watch?v=oHg5SJYRHA0) and move them into the root folder (`./`, aka. current working directory, aka. `ESCALATE_Capture-master/` if downloaded from git). Do not distribute these keys! (Contact a dev for access, or [setup your own](https://github.com/darkreactions/ESCALATE_Capture/wiki/ONBOARDING-LABS))

   Note: [Navigate to the wiki for more information on setting up a new lab or generating additional authentication keys](https://github.com/darkreactions/ESCALATE_Capture/wiki/ONBOARDING-LABS)

2. Ensure that the files 'client_secrets.json' and 'creds.json' are both present in the root folder (`./`, aka. current working directory, aka. `ESCALATE_Capture-master/` if downloaded from git).  The correct folder for these keys is the one which contains the runme.py script.

Running The Code
================

[Detail User Instructions can be found here.](https://docs.google.com/document/d/1RQJvAlDVIfu19Tea23dLUSymLabGfwJtDnZwANtU05s/edit#)

1. Ensure that your computer local time is updated and accurate. If necessary look up how to syncronize your system with internet time.

    * This ensures that the runs have the correct creation information

2. Open the variable container XLSX file of your choice (ex. MIT_SpecificationInterface.xlsx)

3. Update the variables in the XLSX ([see this example for more deatailed instructions](https://drive.google.com/file/d/1OorISnTc4cHbzKQWDPsKaXGcw20fOcIA/view?usp=sharing))

4. **Please ensure that the conditions fall within the indicated ranges and are compatible with the workflow (see ex. [solubility data tabs](https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit?usp=sharing) )** 

    * If the run fails, [see the FAQs](https://docs.google.com/document/d/1RQJvAlDVIfu19Tea23dLUSymLabGfwJtDnZwANtU05s/edit#bookmark=id.8sg0qwagd7yw)!
    
5. Follow additional guidelines for each variable as outlined in .xlsx interface.

6. Execute the script by running 

   `python runme.py <my_specification_file>.xlsx`

   ex. `python runme.py MIT_SpecificationInterface.xlsx`

7. Script will generate files in the "1-Dev" folder of the shared google drive
    * Ensure that desired run information has been generated correctly
    * Move the validated directory to the 2-ExpDev directory ([examples here](https://drive.google.com/drive/u/1/folders/1S6DLLphYBsB-s-HkFddYj1rtZZiyaE0o))
    * Note: The Dev folder should be periodically cleared to ensure that the latest runs can be easily located

ESCALATE Report
=================
* Code for postprocessing can be accessed here: https://github.com/darkreactions/ESCALATE_report
