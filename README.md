Author: Ian Pendleton 
Contact ipendleton .at. haverford.edu

Overview
=================
 
#### Summmary
 This code is intended to provide a simplified means of interfacing between experimental users, NIMBUS robots (using .xls
 files as input), and a final data format that can be parsed and interpreted into a JSON file format.  The code utilizes
 google API at multiple points for data handling, human interfacing and data lookup from manually developed chemical
 dictionaries.  More information about the project for which this code was developed can be found at
 http://sd2perovskite.wikidot.com/project-overview

#### Notes
This toolset was initially designed as a temporary stop gap for the 'robot ready perovskite' workflow and the current version 
of  the 'dark reactions project' (DRP) (https://darkreactions.haverford.edu/).  As time progressed we realized that a
functionality very similar to this code would eventually need to be built into the "recommender" system intended for DRP.  
The result is a multi-purpose code designed with the following challenges in mind:
1) Time delay between initial robot file creation, experimental user data aquistion (recording the actual values used 
in the preparation of reagents), bookkeeping of reaction design (nominal) and experimental (observed/measured), and the final
experimental observables
2) Geospatial isolation of various stakeholders in different timezones responsible for creating and executing the code
and experiments
3) Evolving workflow development in experiment, code changes to adapt to workflow, potential for expanding number of outputs and observables
4) Sampling capable of handling a diversity of the physically accessible chemical space depending on the constraints of each experimental workflow,
reagent components, chemical concentrations, and user constraints

#### Possible useful links
* Specific pydrive API information: https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
* Documentation on pydrive: https://github.com/gsuitedevs/PyDrive
* Secure tokens and authentication: https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

Installation
=============

This code has been tested on MacOS High Sierra and Ubuntu 18.04 LTS.  Though written in python the code interfaces with
Google API and may require debugging for operation on other operating systems and IDEs.

To build the proper environment using anaconda (https://conda.io/docs/user-guide/install/index.html) do the following:

1. Create new python 3.7 environment in conda: `conda create -n my_new_env python=3.7`
1. Execute the following command for each option `conda install <option>`
   * pandas
   * openbabel -c openbabel
   * pip
   * cython
   * numpy
2. Execute the following additional commands `pip install <option>`
   * gspread
   * pydrive
   * xlwt
   * optunity
   * xlutitls
   * matplotlib
   * argparse
<<<<<<< HEAD
3. Download or request access from ipendleton . at . haverford.edu or another member of the perovskite development team for access to the google drive folder of secure keys at: https://drive.google.com/drive/u/1/folders/1cN12AMZSvM5T5yVpFy9tkM_NEle7caQd
=======
3. Download or request access from ipendleton . at . haverford.edu or another member of the perovskite development team for access to the google drive folder of secure keys at: https://drive.google.com/drive/u/0/folders/1yet1CdQxJb4nG0uPCco8rMjqEwpZLeJM
>>>>>>> cae08763f6882a56168ee51c68c1434a06c17e66
4. Unzip the keys and the client_secrets.json file in the main directory where the wf1runme.py script is located

If during the installation process you encounter any issues, please submit a bug report / issue to the git repo or email ipendleton . at . haverford.edu

Running The Code
================

### How to prepare and run a single robot ready perovskite experiment at LBL:
##### Prepare and run a single experiment generation: #####
1. Ensure that your computer local time is updated and accurate. If necessary look up how to syncronize your system with internet time.
2. Open file "wf1runme.py"
3. Update the operating variables in the wf1runme.py file 
4. **Ensure that the conditions fall within the indicated ranges and are compatible with the workflow!!** 
  * (https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit?usp=sharing) 
5. Follow additional guidelines for each variable as outlined in wf1runme.py
  * **Ensure experimental workflow version is correct at the time of script execution!**
  * Feel free to create appropriately named copies of the execution script and upload to the shared folder for future use and sharing (https://drive.google.com/drive/u/1/folders/1kIrsIKe5bWV4PHWltFVyRh12TU-p9j0V)
6. Execute the script by running python3 wf1runme.py
7. Script will generate files in the "Dev" folder of the shared google drive (https://drive.google.com/open?id=11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe)
  * Ensure that desired run information has been generated correctly
  * Move the newly created / validated directory to the ExpDev directory (https://drive.google.com/drive/u/1/folders/1S6DLLphYBsB-s-HkFddYj1rtZZiyaE0o)
8. Update the experimental data for the folder **only while the folder is in the ExpDev directory on Google Drive** (https://drive.google.com/drive/u/1/folders/1S6DLLphYBsB-s-HkFddYj1rtZZiyaE0o) during and after completion of the experiment.
  * Note: The Dev folder will be periodically cleared of old directories, ensure that data are not deleted by only inserting data into files/folders in the ExpDev directory
9. Upon completing the experiment and all necessary record keeping, move the operating directory (current run folder) from the exp_dev directory to the "data" directory (https://drive.google.com/drive/u/1/folders/13xmOpwh-uCiSeJn8pSktzMlr7BaPDo7B)
<<<<<<< HEAD
  * **_Never delete files from the Data folder, EVER_**
=======
  * **_Never delete files from the Data folder, EVER_**
>>>>>>> cae08763f6882a56168ee51c68c1434a06c17e66
