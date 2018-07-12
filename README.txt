##########################################################
#  _        ___           _                              #
# |_)    o   |   _. ._   |_) _  ._   _| |  _ _|_  _  ._  #
# |_) \/ o  _|_ (_| | |  |  (/_ | | (_| | (/_ |_ (_) | | #
#     /                                                  #
##########################################################

Overview of the installation and operation:
1)Establish the python environment by:
  a) conda install <option>
    1) numpy
    2) pandas
    3) openbabel -c openbabel
    4) pip
    5) cython
  b) pip install <option>
    1) gspread
    2) pydrive
    3) xlwt
    4) optunity
    5) xlutitls
    6) matplotlib
    7) argparse

    **Disclaimer** This list is not consolidated and may include packages
    that are not necessary for running this application.  Future versions should include a mac/linux compatible environment.yml 
    along with a more accurate install list.

Prepare and run a single experiment generation:
2) Ensure that your computer local time is updated and accurate. If necessary look up how to syncronize 
  your system with internet time.
3) Open file "ReactionDesign/RunSetup.sh"
4) Update the operating variables in the ReactionDesign/RunSetup.sh file. 
    *** Ensure that the conditions fall within the indicated ranges and are compatible with the workflow!! ** 
4) Follow additional guidelines for each variable as outlined outlined in the RunSetup.sh
  a) **Ensure workflow version is correct at the time of script execution! 
5) execute the script by running ./RunSetup.sh
5) Upload relevant output data on Google Drive after completion of the experiment.  Please use established naming schemes (see wiki for more information - pending)

Please email me at ipendleton .at. haverford.edu for questions

Project Summary:
This toolset was initially designed as a temporary stop gap between the work version of 'dark reactions project' (DRP) at haverford and the addition
of new generalized reaction input on the DRP website. The key challenges addressed were:
  1) Time separation of reaction design (nominal) and experimental (actual) data aquisition.  
  2) Spatial separation of the laboratories running and designing experiments
  3) Diversity of workflow development as a function of three processes, each of which are being designed simultaneously

#### Some useful links for later, possibly
### https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
### https://github.com/gsuitedevs/PyDrive
### https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

Future development:
1) Internet Time instead of local PC
2) Cleanup variable input (argparse) in ReactionDesign script
3) Final JSON file generated through direct parsing of the interface (maybe through django?)
4) Output data graph as a concentration during initial plot? (Is this really that much more useful if the volume is constant? no.)
5) Formic acid displayed as a percent (this is traditional, but technically not better than mmol/M. The % refers to the volume after addition of the first set of reagents, currently 1-4 totaling to "maximumstock" variable)
6) Add individual controls to reagent deadvolume.  --> Development of more nuanced handling of individual wells for each tip of the robot.  Each well has 4 subwells from which the robot draws liquid, typically A and D have different final dead volumes than B and C subwells.
7) Containerize this application for easier distribution.
8) Deeper integration with reagent list.  Establish central resource for reagent list that is not dependent up accurate chemical abbreviations.
9) 