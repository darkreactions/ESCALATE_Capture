## Ian Pendleton
## Dependent upon assumptions made in 0045.perovksitedata.csv
## Many assumptions are denoted at the appropriate location in the code -- some may have been overlooked
## Toward a script for assembling complete reagent inventory from the escalate generated perovskite dataframe

#%%
import pandas as pd
import numpy as np
import os
import sys

INCHI_TO_CHEMNAME = {'null':'null',
'YEJRWHAVMIAJKC-UHFFFAOYSA-N':'Gamma-Butyrolactone',
'IAZDPXIOMUYVGZ-UHFFFAOYSA-N':'Dimethyl sulfoxide',
'BDAGIHXWWSANSR-UHFFFAOYSA-N':'Formic Acid',
'RQQRAHKHDFPBMC-UHFFFAOYSA-L':'Lead Diiodide',
'XFYICZOIWSBQSK-UHFFFAOYSA-N':'Ethylammonium Iodide',
'LLWRXQXPJMPHLR-UHFFFAOYSA-N':'Methylammonium iodide',
'UPHCENSIMPJEIS-UHFFFAOYSA-N':'Phenethylammonium iodide',
'GGYGJCFIYJVWIP-UHFFFAOYSA-N':'Acetamidinium iodide',
'CALQKRVFTWDYDG-UHFFFAOYSA-N':'n-Butylammonium iodide',
'UUDRLGYROXTISK-UHFFFAOYSA-N':'Guanidinium iodide',
'YMWUJEATGCHHMB-UHFFFAOYSA-N':'Dichloromethane',
'JMXLWMIFDJCGBV-UHFFFAOYSA-N':'Dimethylammonium iodide',
'KFQARYBEAKAXIC-UHFFFAOYSA-N':'Phenylammonium Iodide',
'NLJDBTZLVTWXRG-UHFFFAOYSA-N':'t-Butylammonium Iodide',
'GIAPQOZCVIEHNY-UHFFFAOYSA-N':'N-propylammonium Iodide',
'QHJPGANWSLEMTI-UHFFFAOYSA-N':'Formamidinium Iodide',
'WXTNTIQDYHIFEG-UHFFFAOYSA-N':'1,4-Diazabicyclo[2,2,2]octane-1,4-diium Iodide',
'LCTUISCIGMWMAT-UHFFFAOYSA-N':'4-Fluoro-Benzylammonium iodide',
'NOHLSFNWSBZSBW-UHFFFAOYSA-N':'4-Fluoro-Phenethylammonium iodide',
'FJFIJIDZQADKEE-UHFFFAOYSA-N':'4-Fluoro-Phenylammonium iodide',
'QRFXELVDJSDWHX-UHFFFAOYSA-N':'4-Methoxy-Phenylammonium iodide',
'SQXJHWOXNLTOOO-UHFFFAOYSA-N':'4-Trifluoromethyl-Benzylammonium iodide',
'KOAGKPNEVYEZDU-UHFFFAOYSA-N':'4-Trifluoromethyl-Phenylammonium iodide',
'MVPPADPHJFYWMZ-UHFFFAOYSA-N':'chlorobenzene',
'CWJKVUQGXKYWTR-UHFFFAOYSA-N':'Acetamidinium bromide',
'QJFMCHRSDOLMHA-UHFFFAOYSA-N':'Benzylammonium Bromide',
'PPCHYMCMRUGLHR-UHFFFAOYSA-N':'Benzylammonium Iodide',
'XAKAQFUGWUAPJN-UHFFFAOYSA-N':'Beta Alanine Hydroiodide',
'KOECRLKKXSXCPB-UHFFFAOYSA-K':'Bismuth iodide',
'XQPRBTXUXXVTKB-UHFFFAOYSA-M':'Cesium iodide',
'ZMXDDKWLCZADIW-UHFFFAOYSA-N':'Dimethylformamide',
'BCQZYUOYVLJOPE-UHFFFAOYSA-N':'Ethane-1,2-diammonium bromide',
'IWNWLPUNKAYUAW-UHFFFAOYSA-N':'Ethane-1,2-diammonium iodide',
'PNZDZRMOBIIQTC-UHFFFAOYSA-N':'Ethylammonium bromide',
'QWANGZFTSGZRPZ-UHFFFAOYSA-N':'Formamidinium bromide',
'VQNVZLDDLJBKNS-UHFFFAOYSA-N':'Guanidinium bromide',
'VMLAEGAAHIIWJX-UHFFFAOYSA-N':'i-Propylammonium iodide',
'JBOIAZWJIACNJF-UHFFFAOYSA-N':'Imidazolium Iodide',
'RFYSBVUZWGEPBE-UHFFFAOYSA-N':'iso-Butylammonium bromide',
'FCTHQYIDLRRROX-UHFFFAOYSA-N':'iso-Butylammonium iodide',
'UZHWWTHDRVLCJU-UHFFFAOYSA-N':'iso-Pentylammonium iodide',
'MCEUZMYFCCOOQO-UHFFFAOYSA-L':'Lead(II) acetate trihydrate',
'ZASWJUOMEGBQCQ-UHFFFAOYSA-L':'Lead(II) bromide',
'ISWNAMNOYHCTSB-UHFFFAOYSA-N':'Methylammonium bromide',
'VAWHFUNJDMQUSB-UHFFFAOYSA-N':'Morpholinium Iodide',
'VZXFEELLBDNLAL-UHFFFAOYSA-N':'n-Dodecylammonium bromide',
'PXWSKGXEHZHFJA-UHFFFAOYSA-N':'n-Dodecylammonium iodide',
'VNAAUNTYIONOHR-UHFFFAOYSA-N':'n-Hexylammonium iodide',
'HBZSVMFYMAOGRS-UHFFFAOYSA-N':'n-Octylammonium Iodide',
'FEUPHURYMJEUIH-UHFFFAOYSA-N':'neo-Pentylammonium bromide',
'CQWGDVVCKBJLNX-UHFFFAOYSA-N':'neo-Pentylammonium iodide',
'IRAGENYJMTVCCV-UHFFFAOYSA-N':'Phenethylammonium bromide',
'UXWKNNJFYZFNDI-UHFFFAOYSA-N':'piperazine dihydrobromide',
'QZCGFUVVXNFSLE-UHFFFAOYSA-N':'Piperazine-1,4-diium iodide',
'HBPSMMXRESDUSG-UHFFFAOYSA-N':'Piperidinium Iodide',
'IMROMDMJAWUWLK-UHFFFAOYSA-N':'Poly(vinyl alcohol), Mw89000-98000, >99% hydrolyzed)',
'QNBVYCDYFJUNLO-UHDJGPCESA-N':'Pralidoxime iodide',
'UMDDLGMCNFAZDX-UHFFFAOYSA-O':'Propane-1,3-diammonium iodide',
'VFDOIPKMSSDMCV-UHFFFAOYSA-N':'Pyrrolidinium Bromide',
'DMFMZFFIQRMJQZ-UHFFFAOYSA-N':'Pyrrolidinium Iodide',
'DYEHDACATJUKSZ-UHFFFAOYSA-N':'Quinuclidin-1-ium bromide',
'LYHPZBKXSHVBDW-UHFFFAOYSA-N':'Quinuclidin-1-ium iodide',
'UXYJHTKQEFCXBJ-UHFFFAOYSA-N':'tert-Octylammonium iodide',
'BJDYCCHRZIFCGN-UHFFFAOYSA-N':'Pyridinium Iodide',
'ZEVRFFCPALTVDN-UHFFFAOYSA-N':'Cyclohexylmethylammonium iodide',
'WGYRINYTHSORGH-UHFFFAOYSA-N':'Cyclohexylammonium iodide',
'XZUCBFLUEBDNSJ-UHFFFAOYSA-N':'Butane-1,4-diammonium Iodide',
'RYYSZNVPBLKLRS-UHFFFAOYSA-N':'1,4-Benzene diammonium iodide',
'DWOWCUCDJIERQX-UHFFFAOYSA-M':'5-Azaspiro[4.4]nonan-5-ium iodide',
'YYMLRIWBISZOMT-UHFFFAOYSA-N':'Diethylammonium iodide',
'UVLZLKCGKYLKOR-UHFFFAOYSA-N':'2-Pyrrolidin-1-ium-1-ylethylammonium iodide',
'BAMDIFIROXTEEM-UHFFFAOYSA-N':'N,N-Dimethylethane- 1,2-diammonium iodide',
'JERSPYRKVMAEJY-UHFFFAOYSA-N':'N,N-dimethylpropane- 1,3-diammonium iodide',
'NXRUEVJQMBGVAT-UHFFFAOYSA-N':'N,N-Diethylpropane-1,3-diammonium iodide',
'PBGZCCFVBVEIAS-UHFFFAOYSA-N':'Di-isopropylammonium iodide',
'QNNYEDWTOZODAS-UHFFFAOYSA-N':'4-methoxy-phenethylammonium-iodide',
'N/A':'None'}

INCHI_TO_ABBR = {'null':'null',
'YEJRWHAVMIAJKC-UHFFFAOYSA-N':'GBL',
'IAZDPXIOMUYVGZ-UHFFFAOYSA-N':'DMSO',
'BDAGIHXWWSANSR-UHFFFAOYSA-N':'FAH',
'RQQRAHKHDFPBMC-UHFFFAOYSA-L':'PbI2',
'XFYICZOIWSBQSK-UHFFFAOYSA-N':'EtNH3I',
'LLWRXQXPJMPHLR-UHFFFAOYSA-N':'MeNH3I',
'UPHCENSIMPJEIS-UHFFFAOYSA-N':'PhEtNH3I',
'GGYGJCFIYJVWIP-UHFFFAOYSA-N':'AcNH3I',
'CALQKRVFTWDYDG-UHFFFAOYSA-N':'n-BuNH3I',
'UUDRLGYROXTISK-UHFFFAOYSA-N':'GnNH3I',
'YMWUJEATGCHHMB-UHFFFAOYSA-N':'DCM',
'JMXLWMIFDJCGBV-UHFFFAOYSA-N':'Me2NH2I',
'KFQARYBEAKAXIC-UHFFFAOYSA-N':'PhenylammoniumIodide',
'NLJDBTZLVTWXRG-UHFFFAOYSA-N':'tButylammoniumIodide',
'GIAPQOZCVIEHNY-UHFFFAOYSA-N':'NPropylammoniumIodide',
'QHJPGANWSLEMTI-UHFFFAOYSA-N':'FormamidiniumIodide',
'WXTNTIQDYHIFEG-UHFFFAOYSA-N':'Dabcoiodide',
'LCTUISCIGMWMAT-UHFFFAOYSA-N':'4FluoroBenzylammoniumIodide',
'NOHLSFNWSBZSBW-UHFFFAOYSA-N':'4FluoroPhenethylammoniumIodide',
'FJFIJIDZQADKEE-UHFFFAOYSA-N':'4FluoroPhenylammoniumIodide',
'QRFXELVDJSDWHX-UHFFFAOYSA-N':'4MethoxyPhenylammoniumIodide',
'SQXJHWOXNLTOOO-UHFFFAOYSA-N':'4TrifluoromethylBenzylammoniumIodide',
'KOAGKPNEVYEZDU-UHFFFAOYSA-N':'4TrifluoromethylPhenylammoniumIodide',
'MVPPADPHJFYWMZ-UHFFFAOYSA-N':'CBz',
'CWJKVUQGXKYWTR-UHFFFAOYSA-N':'AcNH3Br',
'QJFMCHRSDOLMHA-UHFFFAOYSA-N':'benzylammoniumbromide',
'PPCHYMCMRUGLHR-UHFFFAOYSA-N':'BenzylammoniumIodide',
'XAKAQFUGWUAPJN-UHFFFAOYSA-N':'betaAlanineHydroiodide',
'KOECRLKKXSXCPB-UHFFFAOYSA-K':'BiI3',
'XQPRBTXUXXVTKB-UHFFFAOYSA-M':'CsI',
'ZMXDDKWLCZADIW-UHFFFAOYSA-N':'DMF',
'BCQZYUOYVLJOPE-UHFFFAOYSA-N':'EthylenediamineDihydrobromide',
'IWNWLPUNKAYUAW-UHFFFAOYSA-N':'EthylenediamineDihydriodide',
'PNZDZRMOBIIQTC-UHFFFAOYSA-N':'EtNH3Br',
'QWANGZFTSGZRPZ-UHFFFAOYSA-N':'FABr',
'VQNVZLDDLJBKNS-UHFFFAOYSA-N':'GnNH3Br',
'VMLAEGAAHIIWJX-UHFFFAOYSA-N':'iPropylammoniumIodide',
'JBOIAZWJIACNJF-UHFFFAOYSA-N':'ImidazoliumIodide',
'RFYSBVUZWGEPBE-UHFFFAOYSA-N':'iButylammoniumBromide',
'FCTHQYIDLRRROX-UHFFFAOYSA-N':'iButylammoniumIodide',
'UZHWWTHDRVLCJU-UHFFFAOYSA-N':'IPentylammoniumIodide',
'MCEUZMYFCCOOQO-UHFFFAOYSA-L':'LeadAcetate',
'ZASWJUOMEGBQCQ-UHFFFAOYSA-L':'PbBr2',
'ISWNAMNOYHCTSB-UHFFFAOYSA-N':'Methylammoniumbromide',
'VAWHFUNJDMQUSB-UHFFFAOYSA-N':'MorpholiniumIodide',
'VZXFEELLBDNLAL-UHFFFAOYSA-N':'nDodecylammoniumBromide',
'PXWSKGXEHZHFJA-UHFFFAOYSA-N':'nDodecylammoniumIodide',
'VNAAUNTYIONOHR-UHFFFAOYSA-N':'nHexylammoniumIodide',
'HBZSVMFYMAOGRS-UHFFFAOYSA-N':'nOctylammoniumIodide',
'FEUPHURYMJEUIH-UHFFFAOYSA-N':'neoPentylammoniumBromide',
'CQWGDVVCKBJLNX-UHFFFAOYSA-N':'neoPentylammoniumIodide',
'IRAGENYJMTVCCV-UHFFFAOYSA-N':'Phenethylammoniumbromide',
'UXWKNNJFYZFNDI-UHFFFAOYSA-N':'PiperazinediiumDiBromide',
'QZCGFUVVXNFSLE-UHFFFAOYSA-N':'PiperazinediiumDiodide',
'HBPSMMXRESDUSG-UHFFFAOYSA-N':'PiperidiniumIodide',
'IMROMDMJAWUWLK-UHFFFAOYSA-N':'PVA',
'QNBVYCDYFJUNLO-UHDJGPCESA-N':'PralidoximeIodide',
'UMDDLGMCNFAZDX-UHFFFAOYSA-O':'Propane13diammoniumIodide',
'VFDOIPKMSSDMCV-UHFFFAOYSA-N':'pyrrolidiniumBromide',
'DMFMZFFIQRMJQZ-UHFFFAOYSA-N':'PyrrolidiniumIodide',
'DYEHDACATJUKSZ-UHFFFAOYSA-N':'QuinuclidiniumBromide',
'LYHPZBKXSHVBDW-UHFFFAOYSA-N':'QuinuclidiniumIodide',
'UXYJHTKQEFCXBJ-UHFFFAOYSA-N':'TertOctylammoniumIodide',
'BJDYCCHRZIFCGN-UHFFFAOYSA-N':'PyridiniumIodide',
'ZEVRFFCPALTVDN-UHFFFAOYSA-N':'CyclohexylmethylammoniumIodide',
'WGYRINYTHSORGH-UHFFFAOYSA-N':'CyclohexylammoniumIodide',
'XZUCBFLUEBDNSJ-UHFFFAOYSA-N':'Butane14diammoniumIodide',
'RYYSZNVPBLKLRS-UHFFFAOYSA-N':'Benzenediaminedihydroiodide',
'DWOWCUCDJIERQX-UHFFFAOYSA-M':'5Azaspironoiodide',
'YYMLRIWBISZOMT-UHFFFAOYSA-N':'Diethylammoniumiodide',
'UVLZLKCGKYLKOR-UHFFFAOYSA-N':'2Pyrrolidin1ium1ylethylammoniumiodide',
'BAMDIFIROXTEEM-UHFFFAOYSA-N':'NNDimethylethane12diammoniumiodide',
'JERSPYRKVMAEJY-UHFFFAOYSA-N':'NNdimethylpropane13diammoniumiodide',
'NXRUEVJQMBGVAT-UHFFFAOYSA-N':'NNDiethylpropane13diammoniumiodide',
'PBGZCCFVBVEIAS-UHFFFAOYSA-N':'Diisopropylammoniumiodide',
'QNNYEDWTOZODAS-UHFFFAOYSA-N':'4methoxyphenethylammoniumiodide',
'N/A':'None'}

def UID_generator():
    pass

def build_conc_df(df):
    '''
    Takes in perovskite dataframe and returns a list of "first runs" for a given set of reagents.  
    These 'first runs' are often representative of the maximum solubility limits of a given space.  
    Likely there will be some strangeness in the first iteration that requires tuning of these filters.

    Assumptions: 
    1. ommitting reagents 4-5 for "uniqueness" comparison
    2. need to generalize to use experimental volumes to determing which experiments use which reagents
    3. definitely is missing some of the unique reagents (some are performed at various concetnrations, not just hte first)
    
    Filters are explained in code
    '''
    # Only consider runs where the workflow are equal to 1.1 (the ITC method after initial development)
    df = df[df['_raw_ExpVer'] == 1.1].reset_index(drop=True)

    # only reaction that use GBL as a solvent (1:1 comparisons -- DMF and other solvents could convolute analysis)    
    #perov = perov[perov['_raw_reagent_0_chemicals_0_InChIKey'] == "YEJRWHAVMIAJKC-UHFFFAOYSA-N"].reset_index(drop=True)    

    # removes some anomalous entries with dimethyl ammonium still listed as the organic.
    #perov = perov[perov['_rxn_organic-inchikey'] != 'JMXLWMIFDJCGBV-UHFFFAOYSA-N'].reset_index(drop=True)

    # build a list of all unique combinations of inchi keys for the remaining dataset
    experiment_inchis_df = df.filter(regex='_raw_reagent.*.InChIKey')
    experiment_inchis = (experiment_inchis_df.columns.values)
    experiment_inchis_df = pd.concat([df['name'], experiment_inchis_df], axis=1)
    ignore_list = ['name']

    df.set_index('name', inplace=True)

    # clean up blanks, and bad entries for inchikeys, return date sorted df
    experiment_inchis_df.replace(0.0, np.nan, inplace=True)
    experiment_inchis_df.replace(str(0), np.nan, inplace=True)
    experiment_inchis_df.set_index('name', inplace=True)
    experiment_inchis_df.sort_index(axis=0, inplace=True)

    # find extra reagents (not present in any initial testing runs) (i.e. experiments with zeroindex-reagents 2 < x > 5)
    secondary_reagent_columns = []
    for column in experiment_inchis_df.columns:
        if column in ignore_list:
            pass
        else:
            reagent_num = int(column.split("_")[3]) # 3 is the value of the split for reagent num
            if reagent_num > 10 and reagent_num < 11:
                secondary_reagent_columns.append(column)
    experiment_inchis_df.drop(secondary_reagent_columns, axis=1, inplace=True) 
    experiment_inchis_df.drop_duplicates(inplace=True)
#    experiment_inchis_df = pd.concat([df, experiment_inchis_df], axis=1, join='inner')
    experiment_inchis_df['name'] = experiment_inchis_df.index

    # get the concentration of the relevant associated inchi keys for all included reageagents

    def get_chemical_conc(reagent, inchi, index):
        reagent_inorg_header = f'_raw_reagent_{reagent}_v1-conc_{inchi}'
        try:
            inorg_conc = df.loc[index, reagent_inorg_header]
        except:
            inorg_conc = 0
        return inorg_conc
    
    
    prototype_df = experiment_inchis_df.copy()
    for column in experiment_inchis_df.columns:
        if column in ignore_list:
            pass
        else:
            column_name_split = column.split("_")
            new_column_name = '_'.join(column_name_split[:6]) + '_v1conc'
            reagent_num = column.split("_")[3]
            prototype_df[new_column_name] = experiment_inchis_df.apply(lambda x: get_chemical_conc(reagent_num, x[column], x['name']), axis=1)
    prototype_df = pd.concat([df['_rxn_organic-inchikey'], prototype_df], axis=1, join='inner')
    return prototype_df


def get_tray_set(rxn_uids):
    '''
    take a rxn_uid and returns the tray
    '''
    tray_uids = {}
    for item in rxn_uids:
        tray_uid = item.rsplit('_', 1)[0]
        tray_uids[tray_uid] = item
    return(tray_uids)


def get_unique_volumes(perovskite_df):
    '''
    Get the volume amounts from the downselected unique reagent preparations
    '''
    rxn_uids = perovskite_df['name'].tolist()
    tray_uids = get_tray_set(rxn_uids)

    unique_df = perovskite_df.loc[perovskite_df['name'].isin(tray_uids.values())]

    volume_columns = [column for column in unique_df if 'volume' in column]

    volume_columns = [x for x in volume_columns if 'units' not in x]
    volume_columns.extend(['name','_rxn_organic-inchikey'])
    vol_df = unique_df[volume_columns]
    vol_df.to_csv('unique_reagents_preps.csv')


def all_unique_experiments_v0(dataset_csv):
    '''
    Reads in most recent perovskite dataframe and returns dictionary 
    of structure {organic_inchi: {(Chemical-Inchi, Chemical-Name, concentration) x 3}} 
    one nested dictionary for each inorganic, organic-1, and organic-2

    :param perovskite_csv: perovskite dataframe generated using version 0.7 of the report code
    '''
#    if os.path.exists('0045.perovskitedata.csv'):
#    else:
#        print('Need to included perovskitedata.csv cranks 28-40')
#        sys.exit()
    perovskite_df = pd.read_csv(dataset_csv, skiprows=4, low_memory=False)
    conc_df = build_conc_df(perovskite_df)

    get_unique_volumes(perovskite_df)

    conc_df.fillna(value='null', inplace=True)
    conc_dict_out = {}
    for index, row in conc_df.iterrows():
        conc_dict_out[index] = {}
        conc_dict_out[index]['chemical_info'] = {}
        conc_dict_out[index]['chemical_info']['solvent'] = (conc_df.loc[index,'_raw_reagent_0_chemicals_0_InChIKey'], 
                                                            INCHI_TO_ABBR[conc_df.loc[index,'_raw_reagent_0_chemicals_0_InChIKey']]
                                                            ) 
        conc_dict_out[index]['chemical_info']['inorganic'] = (conc_df.loc[index,'_raw_reagent_1_chemicals_0_InChIKey'], 
                                                            INCHI_TO_ABBR[conc_df.loc[index,'_raw_reagent_1_chemicals_0_InChIKey']],
                                                            conc_df.loc[index,'_raw_reagent_1_chemicals_0_v1conc']                                                               
                                                            ) 
        conc_dict_out[index]['chemical_info']['organic-1'] = (conc_df.loc[index,'_raw_reagent_1_chemicals_1_InChIKey'], 
                                                            INCHI_TO_ABBR[conc_df.loc[index,'_raw_reagent_1_chemicals_1_InChIKey']],
                                                            conc_df.loc[index,'_raw_reagent_1_chemicals_1_v1conc']                                                               
                                                            ) 
        conc_dict_out[index]['chemical_info']['organic-2'] = (conc_df.loc[index,'_raw_reagent_2_chemicals_0_InChIKey'], 
                                                            INCHI_TO_ABBR[conc_df.loc[index,'_raw_reagent_2_chemicals_0_InChIKey']],
                                                            conc_df.loc[index,'_raw_reagent_2_chemicals_0_v1conc']                                                               
                                                            ) 
        conc_dict_out[index]['organic_inchi'] = conc_df.loc[index, '_rxn_organic-inchikey']
    return conc_dict_out

#%%
#%%
# Section 2
## The following function normalizes differences in the state space concentrations
## and sets all of the axes to the same scale. This might allow for a different overlaying 
## of various state spaces

def _compute_proportional_conc(perovRow, v1=True, chemtype='organic'):
    """Compute the concentration of acid, inorganic, or acid for a given row of a crank dataset
    TODO: most of this works, just need to test before deploy
    
    Intended to be pd.DataFrame.applied over the rows of a crank dataset
    
    :param perovRow: a row of the crank dataset
    :param v1: use v1 concentration or v0 
    :param chemtype: in ['organic', 'inorganic', 'acid']
    
    
    Currently hard codes inorganic as PbI2 and acid as FAH. TODO: generalize
    """
    inchis = {
        'organic': perovRow['_rxn_organic-inchikey'],
        # Inorganic assumes PbI2, so far the only inorganic in the dataset
        'inorganic': 'RQQRAHKHDFPBMC-UHFFFAOYSA-L',
        ## acid assumes FAH (as of writing this the only one in the dataset)
        'acid': 'BDAGIHXWWSANSR-UHFFFAOYSA-N'
    }
    speciesExperimentConc = perovRow[f"{'_rxn_M_' if v1 else '_rxn_v0-M_'}{chemtype}"]
    
    reagentConcPattern = f"_raw_reagent_[0-9]_{'v1-' if v1 else ''}conc_{inchis[chemtype]}"
    speciesReagentConc = perovRow.filter(regex=reagentConcPattern)
    
    if speciesExperimentConc == 0: 
        return speciesExperimentConc
    else: 
        return speciesExperimentConc / np.max(speciesReagentConc)

def _prepare(shuffle=0, deep_shuffle=0):
    ''' reads in perovskite dataframe and returns only experiments that meet specific criteria

    --> Data preparation occurs here
    criteria for main dataset include experiment version 1.1 (workflow 1 second generation), only
    reactions that use GBL, and 
    '''
    perov = pd.read_csv(os.path.join(VERSION_DATA_PATH, CRANK_FILE), skiprows=4, low_memory=False)
    perov = perov[perov['_raw_ExpVer'] == 1.1].reset_index(drop=True)

    # only reaction that use GBL as a solvent (1:1 comparisons -- DMF and other solvents could convolute analysis)    
    perov = perov[perov['_raw_reagent_0_chemicals_0_InChIKey'] == "YEJRWHAVMIAJKC-UHFFFAOYSA-N"].reset_index(drop=True)    

    # removes some anomalous entries with dimethyl ammonium still listed as the organic.
    perov = perov[perov['_rxn_organic-inchikey'] != 'JMXLWMIFDJCGBV-UHFFFAOYSA-N'].reset_index(drop=True)

    #We need to know which reactions have no succes and which have some
    organickeys = perov['_rxn_organic-inchikey']
    uniquekeys = organickeys.unique()

    df_key_dict = {}
    #find an remove all organics with no successes (See SI for reasoning)
    for key in uniquekeys:
        #build a dataframe name by the first 10 characters of the inchi containing all rows with that inchi
        df_key_dict[str(key)] = perov[perov['_rxn_organic-inchikey'] == key]
    all_groups = []
    successful_groups = []
    failed_groups = []
    for key, value in df_key_dict.items():
        all_groups.append(key)
        if 4 in value['_out_crystalscore'].values.astype(int):
            successful_groups.append(key)
        else:
            failed_groups.append(key)

    #only grab reactions where there were some recorded successes in the amine grouping
    successful_perov = (perov[perov['_rxn_organic-inchikey'].isin(successful_groups)])
    successful_perov = successful_perov[successful_perov['_rxn_organic-inchikey'] != 'JMXLWMIFDJCGBV-UHFFFAOYSA-N'].reset_index(drop=True)

    # we need to do this so we can drop nans and such while keeping the data consistent
    # we couldnt do this on the full perov data since dropna() would nuke the entire dataset (rip)
    all_columns = successful_perov.columns
    
    full_data = successful_perov[all_columns].reset_index(drop=True)

    full_data = full_data.fillna(0).reset_index(drop=True)
    successful_perov = full_data[full_data['_out_crystalscore'] != 0].reset_index(drop=True)
    
    successful_perov.rename(columns={"_raw_v0-M_acid": "_rxn_v0-M_acid", "_raw_v0-M_inorganic": "_rxn_v0-M_inorganic", "_raw_v0-M_organic":"_rxn_v0-M_organic"}, inplace=True)

    return successful_perov