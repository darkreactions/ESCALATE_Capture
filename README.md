Author: Ian Pendleton 
Contact ipendleton .at. haverford.edu

Overview
=================
A detailed description of the current functionality and logic for this code can be found here: https://docs.google.com/document/d/1vF4mq76mNutCdTCtKAUu91RTm3IS5LX4STxJ0t1JF5U/edit#

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

If during the installation process you encounter any issues, please submit a bug report / issue to https://github.com/darkreactions/ESCALATE_Capture

Running The Code
================

1. Ensure that your computer local time is updated and accurate. If necessary look up how to syncronize your system with internet time.
2. Open the variable container XLSX file of your choice (ex. WF1_template.xlsx)
3. Update the variables in the XLSX
4. **Please ensure that the conditions fall within the indicated ranges and are compatible with the workflow (see solubility data tabs)** 
  * (https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit?usp=sharing) 
5. Follow additional guidelines for each variable as outlined in WF1_template.xlsx
  * Please create appropriately named copies of the variables.XLSX file and upload to the shared folder for future use (https://drive.google.com/drive/u/1/folders/1kIrsIKe5bWV4PHWltFVyRh12TU-p9j0V)
6. Execute the script by running `python runme.py WF1_template.xlsx`
7. Script will generate files in the "Dev" folder of the shared google drive (https://drive.google.com/open?id=11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe)
  * Ensure that desired run information has been generated correctly
  * Move the validated directory to the ExpDev directory (https://drive.google.com/drive/u/1/folders/1S6DLLphYBsB-s-HkFddYj1rtZZiyaE0o)
  * Note: The Dev folder will be periodically cleared of old directories, ensure that data are not deleted by only inserting data into files/folders in the ExpDev directory

**_Never delete files from the Data folder, EVER_**

#### Possible useful links
* Specific pydrive API information: https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
* Documentation on pydrive: https://github.com/gsuitedevs/PyDrive
* Secure tokens and authentication: https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process
