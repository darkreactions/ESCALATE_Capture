## Author Ian Pendleton
#%%
import os 
import pandas as pd 

#%%


def get_link_files(dir_files):
    relevant_files = []
    for linkfile in dir_files:
        if 'link.csv' in linkfile:
            relevant_files.append(linkfile)
    return(relevant_files)

def multi_column_max(primary_column, secondary_column):
    df = pd.concat([primary_column, secondary_column], axis=1)
    max_primary = df[primary_column.name].max()
    secondary_working_df = df.loc[df[primary_column.name] == max_primary]
    max_secondary = secondary_working_df[secondary_column.name].max()
    return (max_primary, max_secondary)

def state_space_edges(linkcsv):
    link_df = pd.read_csv(linkcsv)
    entry_name_1 = linkcsv.split('_')[0]
    entry_name_index = linkcsv.split('_')[1]

    scalar = 1 # fixes off by percent issue from sub-saturated sampling used to geernate spaces
    #formulate the tuple for the acid/organic max node
    max_acid_max_org_tuple = (link_df.loc[4,'_rxn_M_inorganic'],link_df.loc[4,'_rxn_M_organic'],link_df.loc[4,'_rxn_M_acid'])

    #formulate the tuple for the acid/inorganic max node
    max_acid_max_inorg_tuple = (link_df.loc[3,'_rxn_M_inorganic'],link_df.loc[3,'_rxn_M_organic'],link_df.loc[3,'_rxn_M_acid'])

    # chemicals are returned as tuple (inorganic,organic, acid) 
    d = { 
        'uid':entry_name_index,
        'chemical_list':entry_name_1,
        '0_zeros':(0,0,0),
        '1_organic_max': (0,link_df['_rxn_M_organic'].max()*scalar,0),
        '2_inorganic_max': (link_df.loc[0,'_rxn_M_inorganic'],link_df.loc[0,'_rxn_M_organic'],0),
        '3_acid_max':(0,0,link_df['_rxn_M_acid'].max()*scalar),
        '4_max_acid_max_org': max_acid_max_org_tuple,
        '5_max_acid_max_inor': max_acid_max_inorg_tuple
    }
    return d


def run_me():
#    all_files_in_dir = os.listdir('/mnt/d/HaverfordGoogleDrive/ESCALATE_Development/Scripts/Reagent_StateSpaces_Small')
    all_files_in_dir = os.listdir('/Users/ipendleton/HaverDrive/ESCALATE_Development/Scripts/Reagent_StateSpaces_Small')
    link_files = get_link_files(all_files_in_dir)
    print(link_files)
    state_space_node_dicts = []
    for working_file in link_files:
        conc_maxs_dict = state_space_edges(working_file)
        state_space_node_dicts.append(conc_maxs_dict)
    state_space_node_df =  pd.DataFrame(state_space_node_dicts)
    state_space_node_df.set_index('uid', inplace=True)
    return(state_space_node_df)



if __name__ == "__main__":
    run_me().to_csv('All_reagent_tuples.csv')

#%%
