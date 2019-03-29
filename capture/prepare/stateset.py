import pandas as pd

def augdescriptors(inchikeys, rxndict, erdfrows):
    #bring in the inchi key based features for a left merge
    with open('perov_desc.csv', 'r') as my_descriptors:
       descriptor_df=pd.read_csv(my_descriptors) 
    descriptor_df=inchikeys.merge(descriptor_df, left_on='_rxn_organic-inchikey', right_on='_raw_inchikey', how='inner')
    cur_list = [c for c in descriptor_df.columns]
#    cur_list = [c for c in descriptor_df.columns if 'raw' not in c]
#    cur_list_raw = [c for c in descriptor_df.columns if 'raw' in c]
    descriptor_df = descriptor_df[cur_list]
    descriptor_df.drop(columns=['_rxn_organic-inchikey'], inplace=True)
    ds1 = [rxndict['duratation_stir1']]*erdfrows
    ds1df = pd.DataFrame(ds1, columns=['_rxn_mixingtime1S'])
    ds2 = [rxndict['duratation_stir2']]*erdfrows
    ds2df = pd.DataFrame(ds2, columns=['_rxn_mixingtime2S'])
    dr = [rxndict['duration_reaction']]*erdfrows
    drdf = pd.DataFrame(dr, columns=['_rxn_reactiontimeS'])
    sr1 = [rxndict['stirrate']]*erdfrows
    sr1df = pd.DataFrame(sr1, columns=['_rxn_stirrateRPM'])
    t = [rxndict['temperature2_nominal']]*erdfrows
    tdf = pd.DataFrame(t, columns=['_rxn_temperatureC'])
    outdf = pd.concat([inchikeys, ds1df,ds2df,drdf,sr1df,tdf,descriptor_df], axis=1)
    return(outdf)