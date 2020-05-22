**Authors: Ian Pendleton, Michael Tynes, Aaron Dharna**

**Science Contact:** ipendleton .at. haverford.edu

**Technical Debugging:** mtynes .at. fordham.edu, adharna .at. fordham.edu


Overview
=================
A detailed description of the current functionality and logic for this code can be found here: https://docs.google.com/document/d/1vF4mq76mNutCdTCtKAUu91RTm3IS5LX4STxJ0t1JF5U/edit#

User Documents are being updated and can be found here: https://docs.google.com/document/d/1RQJvAlDVIfu19Tea23dLUSymLabGfwJtDnZwANtU05s/edit#heading=h.uzjqm9vtn09j

Installation
=============

This code has been tested on MacOS High Sierra and Ubuntu 18.04 LTS.  Though written in python the code interfaces with
Google API and may require debugging for operation on other operating systems and IDEs.

To build the proper environment using anaconda (https://conda.io/docs/user-guide/install/index.html) do the following:

1. Deactivate any current conda instance: `conda deactivate`
2. Create new python 3.7 environment in conda: `conda create -n myenv python=3.7`
3. Execute the following additional command: `pip install -r requirements.txt`
4. Download or request access from ipendleton . at . haverford.edu for access to the google drive folder of secure keys at: https://drive.google.com/drive/u/1/folders/1cN12AMZSvM5T5yVpFy9tkM_NEle7caQd
5. Place the keys in main folder of the ESCALATE_Capture code.

* If you need to run the mathematica sampler please install wolfram engine on your operating system.  Follow instructions here: https://www.wolfram.com/engine/
* Once installed please change the sampler option from 'default' to 'wolfram' in the file capture/devconfig.py

If during the installation process you encounter any issues, please submit a bug report / issue to https://github.com/darkreactions/ESCALATE_Capture

Installation on Windows:
1. Download and install anaconda for windows here: https://docs.anaconda.com/anaconda/install/windows/
2. Download and unzip the zip file (or use git clone) of the ESCALATE capture code https://github.com/darkreactions/ESCALATE_Capture/archive/master.zip
3. download and install wolfram engine https://www.wolfram.com/engine/ (Be sure to activate!!! https://support.wolfram.com/46069)

   * Wolfram occasionally updates the engine.  Default is set to detect version 12.1.  If you receive a 'wolfram client' not found error, please check the linux_path in ./capture/devconfig.py 

4. Open a miniconda window and navigate to the unzipped ESCALATE_Capture-master folder
5. Create new python 3.7 environment in conda: `conda create -n myenv python=3.7`
6. Activate the new environment: `conda activate myenv`
7. Execute the following additional command: `pip install -r requirements.txt`
8. Download or request access keys, add them to the ESCALATE_capture-master folder (these are named 'client_secrets.json' and creds.json')
9. Follow instructions on Running the code below

Running The Code
================

1. Ensure that your computer local time is updated and accurate. If necessary look up how to syncronize your system with internet time.
2. Open the variable container XLSX file of your choice (ex. MIT_SpecificationInterface.xlsx)
3. Update the variables in the XLSX ([see this example for more deatailed instructions](https://drive.google.com/file/d/1OorISnTc4cHbzKQWDPsKaXGcw20fOcIA/view?usp=sharing))
4. **Please ensure that the conditions fall within the indicated ranges and are compatible with the workflow (see solubility data tabs)** 
  * (https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit?usp=sharing) 
5. Follow additional guidelines for each variable as outlined in MIT_SpecificationInterface.xlsx
6. Execute the script by running `python runme.py MIT_SpecificationInterface.xlsx`
7. Script will generate files in the "Dev" folder of the shared google drive
  * Ensure that desired run information has been generated correctly
  * Move the validated directory to the ExpDev directory (https://drive.google.com/drive/u/1/folders/1S6DLLphYBsB-s-HkFddYj1rtZZiyaE0o)
  * Note: The Dev folder should be periodically cleared to ensure that the latest runs can be easily located

ESCALATE Report
=================
* Code for working up the data can be accessed here: https://github.com/darkreactions/ESCALATE_report
* The report code will soon be merged with Capture, but for now are maintained as separate repositories
