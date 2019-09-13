RELEASE HISTORY
===============

2.54 (2019-09-13)
-----------------------------
  * Union - Intersect mathematica sampling (now sampler 1.2)
  * Small fixes to default template
  * adjusted devconfig defaults

2.53 (2019-08-16)
----------------------------- 
  * Native model reporting for escalate and manual runs
  * Syntax fixes
  * Pep8 fixes

2.52 (2019-08-01)
-----------------------------
  * Reimplemented WF3 support
  * Minor bug fixes for windows machines
  * Minor bug fixes for HC support
  * Added 'new folders' as an option to devconfig
  * Updated templates to match current wf
  * new data validation on chemical sheets (lives on google)

2.51 (2019-07-22)
-----------------------------
  * Abstracted template with wrapper
  * (e.g. user controls 'reagent' names)
  * renamed interaction files to be more general
  * (e.g. CrystalScore --> ObservationInterface)
  * Added in manual specification of experiments
  * Protected cells the user is not allowed to edit
  * Added more clarity to UI
  * Added MIT as a supported lab with a (somewhat) unique pipeline

2.5 (2019-06-17)
-----------------------------
  * New grid sampling in place of quasirandom sampling (uses mathematica in 2.5) #32 #48
  * No grid sampling for WF3 - must set "default" sampling in devconfig 
  * updated templates
  * improved document readability

2.4 (2019-04-20)
----------------------------
  * Meta data patch
  * Updated versioning 
  * updated templates
  * WF3 support added and tested

2.3 (2019-04-16)
----------------------------
  * Added ECL support
  * Reagents can be specified by model OR user input (not both)
  * Simplified chemical specification through inclusion in reagent list
  * Updated templates to reflect new interface architecture 
  * Cleaned up files dumping to google drive

2.2 (2019-03-27)
----------------------------
  * Reorganized code for easier modification
  * Clarified variable usage from dictionaries
  * Clarified variables -- no hidden hardcodes
  * Linearized code
  * Redesigned UI and improved descriptions
  * Added development template which includes all relevant variables
  * Updated Readme, History, and templates.xls for end users
  * Extended code to function with any combination of 7 reagent solutions
  * Developer template and multiple user templates produced
  * Generalized reagent interface JSON file for 7 reagents
  * JSON generator updated for 7 reagents
  * Debugged multiple amines / tray (including with report functionality)
  * WARNING -- plotter is currently broken

2.1 (2019-02-27)
----------------------------
  * Removed user variable entry from code to XLS file
  * Organized code into appropriate sections for clarity
  * Deconvoluted variable relationships (made dictionaries easier to work with)

2.0.1 (2018-11-07)
---------------------------
  * Fixed FAH to reagents 6,7
  * Debugging fixes to generator
  * Additional CP automation

2.0 (2018-11-07)
---------------------------
  * Bug fixes
  * Added capacity for additional reagent
  * added volume correction to workflow which records the final prepared volume of the stock solution in addition nominal and actual solvent measured out during reagent preparation
  * Organized code into smaller portions prior to distribution and forking for challenge problem
  * Significant revisions to the sampling regime
  * Flexibility for multiple experiments using different chemicals
  * New experimental data interface for support for more reagents
  * Additional data output for post processing
  * Example scripts for user execution
  * Updated user interface (execution script) with a bit more flexibility
  * Improved logging --> More work still pending

1.2 (2018-08-01)
--------------------------
  * Organized code, fixed some initial bugs in the data generation, automated and distributed working version of the code to stakeholders (zhi, mansoor)

1.1 (2018-07-16)
----------------
  * Bug fixes which prevented program from generating potential reactions throughout all of the accessible physical space
  * other minor bug fixes

1.0 (2018-06-10)
----------------
  * Commited first fully functioning version of the experiment generator capable of generating a psuedorandom exploration of the concentrations provided by user
  * Updated associated files for logging and running code
