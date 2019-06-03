# ESCALATE Data Structures

A quick reference for the dictionaries, DataFrames, and classes that are defined inside of ESCALATE.

### Template
**Templates** are Excel spreadsheets used by scientists to specify experiments for ESCALATE. 
Many of the data structures in ESCALATE are defined based on the **Template** of a given run. 

A **Template** is composed of the following sections:

* **Entity** contains:
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
    
----


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




### Implementation Structures:

- `Vardict`
    - This contains the computer-science related information used in the program. 
      Information from the CLI and devconfig file. 

- `Rxndict`
    - Parses a user-supplied reaction spreadsheet into a dict.
    - See: WF1_DevTemplate.xlsx for an example
    - contains the above info

These two dicts also contain meta-data information specific to each run of the code so that the batches 
  may be uniquely identified

---- 


- `chemdf`
    - Dataframe with chemical information from gdrive
    - https://docs.google.com/spreadsheets/d/1JgRKUH_ie87KAXsC-fRYEw_5SepjOgVt7njjQBETxEg/edit#gid=734961316
    
- `reagentdf`
    - DataFrame with reagent informatin from gdrive
    - 
 
- `climits`
    - pulls Min and Max for each chemical.
    - saves into dict the min and max for each chemical
    - dict of user defined chemical limits (concentrations?)
    - defined in the template excel file for each portion of rxndict
    
- `solventList`
    - defined in devconfig
    
----  

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
 
 ----  
 
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
