RELEASE HISTORY
===============

1.0 (2018-06-10)
----------------
  * Commited first fully functioning version of the experiment generator capable of generating a psuedorandom exploration of the concentrations provided by user
  * Updated associated files for logging and running code

1.1 (2018-07-16)
----------------
  * Bug fixes which prevented program from generating potential reactions throughout all of the accessible physical space
  * other minor bug fixes

1.2 (2018-08-01)
--------------------------
  * Organized code, fixed some initial bugs in the data generation, automated and distributed working version of the code to stakeholders (zhi, mansoor)

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
2.0.1 (2018-11-07)
---------------------------
  * Fixed FAH to reagents 6,7
  * Debugging fixes to generator
  * Additional CP automation

2.1 (2019-02-27)
----------------------------
  * Removed user variable entry from code to XLS file
  * Organized code into appropriate sections for clarity
  * Deconvoluted variable relationships (made dictionaries easier to work with)

2.2 (2019-03-27)
----------------------------
  * Reorganized code for easier modification
  * Clarified valiable usage from dictionaries
  * Linearized code