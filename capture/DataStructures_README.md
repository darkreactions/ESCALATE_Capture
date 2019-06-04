# ESCALATE Variables and Data Structures

A quick reference for the dictionaries, DataFrames, and classes that are defined inside of ESCALATE, as well
as the tables and config files that ESCALATE reads from at runtime.

## Devconfig.py

Devconfig.py exposes the following variables for configuration **Todo: Ian write this part, we can also just document
that file inline and point to it here after generally describing the types of variables that devconfig exposes**

## Tables (Excel + GoogleSheets)

ESCALATE reads from Excel and GoogleSheets files during its execution. They are documented here.

### Template (Excel file)
**Templates** are Excel spreadsheets used by scientists to specify experiments for ESCALATE. 
Many of the data structures in ESCALATE are defined based on the **Template** of a given run. 

A **Template** is composed of the following sections:

- **Entity** contains:
    - software version
    - Lab 
        - e.g. LBL
    - plotter

- **Experiment** contains:
    - `wellcount`
    - for each exp in [1..Max Experiments]: 
        - list of `portions`:
            - [[2, 3, 1], [6, 7]]
            - see `expOverView`
        - list of min/max volumes for each `portion`
            - [[500, 500], [0, 250]]
        - `n_wells`: number of wells in this exp. 
          The sum of `n_wells` over the expriments must equal wellcount

- **Materials** contains: 
    - Chemicals
        - *not implemented yet*
    - Reagents:
        - Format: `Reagent_<i>` (e.g Reagent1)
        - Reagent1 should be solvent. 
        - Can be specified in *one* of two (mutually exclusive) ways:
            - `Reagent_<i>_ID`
                - an ECL Model ID. 
                - see [Reagents worksheet](https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit#gid=1755798808)
             - `Reagent_<i>_checmical_list`
                 - list of chemicals used in reagent_ID_NUMBER
                        - ['PbI2','EtNH3I','GBL']
                - concentrations for reagents in the list above
                    - will have 1 - len(above list)
- **Actions**
    - stirrate
    - temperature of plate
    - etc

### Chemical Inventory (GoogleSheets Workbook)

The Chemical Inventory maintains information on all chemicals and reagents used in ESCALATE. 

It contains two key worksheets: 
- Chemicals
- Reagents
    
Which maintain **TODO: Ian flesh out this section**


    
### Classes

- class `PerovskiteReagent`
    - init Args:
        - reagentVariables: 
            - {'reagent': reagentname,
               'etc': etc
               }
        - rxndict
        - reagent_ID_NUMBER
        - chemdf
        - solventList
    - Member Variables:
        - `name`; str 
            - e.g. 2
        - `chemicals`: list
            - list of the chemicals in this reagent
        - `concs`: dict
            - e.g. {'conc_item1': float concentration }
        - `isPure`: boolean
            - is this purely one chemical
        - `solventNumber`: int
        - `prepTemperature`: int (or float?)
            - reagentVariables["prep_temperature"]
        - `prepStir`: int (or float?)
            - reagentVariables["prep_stirrate"]
        - `prepDuration`: int (or float?)
            - reagentVariables["prep_duration"]
        - `preRxnTime`: int (or float?)
            - reagentVariables["prerxn_temperature"]
        - `prepTempUnits`: str
        - `prepStirUnits`: str
        - `prepDurUnits` : str        
    
    - Member Methods:
        Skipping __init__ helper fns
        
        - Mike's new fn goes here. 

- class ``:

    - init Args:
    
    - Member Variables: 
    
    - Member Methods


### Dictionaries

- `Rxndict`
    - A dict representation of the run's **Template**.
    - The k -> v mapping is of the form Variable -> Value where Variable and Value are columns of the 
    **Template** XLS file.   
    - See: WF1_DevTemplate.xlsx for an example


- `Vardict`
    - Mostly the software engineering related information:  
    i.e. variables defined at the CLI and in the devconfig file. 

The two above dicts also contain meta-data information specific to each run of the code so that the batches 
may be uniquely identified
   
- `rdict`
    - reagent dict
        - e.g. rdict[2] = PerovskiteReagent(...)
        
- `edict`
    - experiment dict <-- Needs new name! 
        - e.g. edict[key] = value 
    - is a subset of `rxndict`
        
Regarding the above two dicts: We should have the internal structure of these match.  
e.g. rdict[] maps to an instanciated Reagent class. However, edict is simply mapping to a subset of rxndict. 
Specifically, the subset of k/v pairs in rxn dict whose key's have 'exp' in the key-string.

- `reagentvariables`
    - local to capture.reagent.buildreagents
    - a subset of rxndict defining a particular reagent
    - keys are things like `item_<i>_formula` or `prep_stirrate`
    - defined for an *individual* reagent and passed to `perovskitereagent.__init__()` as `reactantinfo`
    

- `climits`
    - pulls Min and Max for each chemical.
    - saves into dict the min and max for each chemical
    - dict of user defined chemical limits (concentrations?)
    - defined in the template excel file for each portion of rxndict 
    - **TODO: I don't see any limits in any of the example XLS files... how is this intended to be used?**

### DataFrames

- `chemdf`
    - DataFrame representation of the Chemical Inventory -> Chemicals GoogleSheet.
    - an example can be seen [here](https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit#gid=73496131)
    
- `reagentdf`
    - DataFrame representation of the Chemical Inventory -> Reagents GoogleSheet
    - an example can be seen [here](https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit#gid=203471557)
    
- `erdf`
   - (e)xperiment (r)eagent dataframe
   - Final reagent volumes dataframe
    
- `ermmoldf`
   - (e)xperiment (r)eagent milli-mol dataframe
   - Final reagent mmol dataframe broken down by experiment, protion, reagent, and chemical
    
- `emsumdf`
   - (e)xperiment (r)eagent dataframe
   - Final nominal molarity for each reagent in each well
    
- `expOverVIew`
    - List of `s` -- see above
