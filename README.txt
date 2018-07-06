##########################################################
#  _        ___           _                              #
# |_)    o   |   _. ._   |_) _  ._   _| |  _ _|_  _  ._  #
# |_) \/ o  _|_ (_| | |  |  (/_ | | (_| | (/_ |_ (_) | | #
#     /                                                  #
##########################################################

Overview of the installation and operation:
**Establish the python environment by either:
  a) source the anaconda environment file 
    $$ conda env create -f environment.yml
  b) if the operating system is different than used to generate the .yml (a likely condition) open the .yml 
    in a text editor and install the relevant packages.  **Disclaimer** This list is not consolidated and may include packages
    that are not necessary for running this application.  Future versions of the environment.yml will be more accurate for 
    generating the correct environment.
 or
  c)'pip install' the following packages (at a minimum):
      pip install oauth2client.service_account
      pip install gspread
      pip install argparse
      pip install pydrive

For an individual run generation and workup:
2) Ensure that your computer local time is updated and accurate. If necessary look up how to syncronize 
  your system with internet time.
3) Open file "ReactionDesign/RunSetup.sh"
4) Update the operating variables in the ReactionDesign/RunSetup.sh file. 
    *** Ensure that the conditions fall within the indicated ranges!! ** 
4) Follow additional instructions outlined ReactionDesign/RunSetup.sh
5) Once data has been collected proceed to execute the Workup/CreateDBInput.py
    python CreateDBInput.py 1 
6) Manually upload the generated JSON file associated with the new run to google drive or the relevant
  data storage location.

Please email me at ipendleton@haverford.edu for questions

Project Summary:
This toolset was initially designed as a temporary stopgap between the work version of 'dark reactions project' (DRP) at haverford and the addition
of new generalized reaction input on the DRP website. The key challenges addressed were:
  1) Time separation of reaction design (nominal) and experimental (actual) data aquisition.  
  2) Spatial separation of the laboratories running and designing experiments
  3) Diversity of workflow development as a function of three processes, each of which are being designed simultaneously

#### Some useful links for later, possibly
### https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
### https://github.com/gsuitedevs/PyDrive
### https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

Future development work:
1) Internet Time instead of local PC
2) Cleanup variable input (argparse) in ReactionDesign script