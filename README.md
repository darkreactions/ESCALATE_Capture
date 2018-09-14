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
3) Evolving workflow development in experiment, code changes to adapt to workflow, potential for expanding number of outputs and observatables
4) Optimal sampling of the physically accessible chemical space depending on the constraints of each experimental workflow

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

Download or request access from google drive administrator the client_secrets.json key or access it on the SD2 google
drive. **_Do not distribute this key! (https://drive.google.com/open?id=1UJF-yt3h1J6vOyYls7J_lKcAcFlSTO_l)_**

If during the installation process you encounter any issues, please submit a bug report / issue to the git repo.

Running The Code
================

### How to prepare and run a single robot ready perovskite experiment at LBL:

Prepare and run a single experiment generation:
1) Ensure that your computer local time is updated and accurate. If necessary look up how to syncronize your system with
internet time.

2) Open file "ReactionDesign/RunSetup.sh"

3) Update the operating variables in the ReactionDesign/RunSetup.sh file. 
* **Ensure that the conditions fall within the indicated ranges and are compatible with the workflow!!** 
* (https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit?usp=sharing) 

4) Follow additional guidelines for each variable as outlined outlined in the RunSetup.sh
  * **Ensure experimental workflow version is correct at the time of script execution!**
  * Feel free to create appropriately named copies of the RunSetup.sh script and upload to the shared folder for future use
  and sharing (https://drive.google.com/drive/u/1/folders/1kIrsIKe5bWV4PHWltFVyRh12TU-p9j0V)

5) Execute the script by running ./RunSetup.sh

6) Script will generate files in the "Dev" folder of the shared google drive (https://drive.google.com/open?id=11vIE3oGU77y38VRSu-OQQw2aWaNfmOHe)
  * Ensure that desired run information has been generated correctly
  * Move the newly created / validated directory to the ExpDev directory (https://drive.google.com/drive/u/1/folders/1S6DLLphYBsB-s-HkFddYj1rtZZiyaE0o)

7) Update the experimental data for the folder **only while the folder is in the ExpDev directory on Google Drive**
(https://drive.google.com/drive/u/1/folders/1S6DLLphYBsB-s-HkFddYj1rtZZiyaE0o) during and after completion of the experiment.
  * Note: The Dev folder will be periodically cleared of old directories, ensure that data are not deleted by only 
  inserting data into files/folders in the ExpDev directory

8) Upon completing the experiment and all necessary record keeping, move the operating directory (current run folder) from the 
exp_dev directory to the "data" directory (https://drive.google.com/drive/u/1/folders/13xmOpwh-uCiSeJn8pSktzMlr7BaPDo7B)
  * **_Never delete files from the Data folder, EVER_**


Future Development Ideas
========================
1) Volume Correction for accurate molarity calculation
1) Fork / toggle for challenge problem
1) Internet Time instead of local PC
2) Cleanup variable input (argparse) in ReactionDesign script
3) Final JSON file generated through direct parsing of the interface (maybe through django?)
4) Output data graph as a concentration during initial plot? (Is this really that much more useful if the volume is constant? no.)
5) Formic acid displayed as a percent (this is traditional, but technically not better than mmol/M. The % refers to the volume after addition of the first set of reagents, currently 1-4 totaling to "maximumstock" variable)
6) Add individual controls to reagent deadvolume.  --> Development of more nuanced handling of individual wells for each tip of the robot.  Each well has 4 subwells from which the robot draws liquid, typically A and D have different final dead volumes than B and C subwells.
7) Containerize this application for easier distribution.
8) Deeper integration with reagent list.  Establish central resource for reagent list that is not dependent up accurate chemical abbreviations.
9) **Expand .xls generation to 7 reagents in the correct format**
10) **Separate workflow for HC (possibly long term, ECL)**
11) 
