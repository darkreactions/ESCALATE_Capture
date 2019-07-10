"""Useful stuff that has no proper home
"""
import pandas as pd
import re

from capture.devconfig import REAGENT_ALIAS


def get_explicit_experiments(rxnvarfile):
    """Extract reagent volumes for the manually specified experiments, if there are any.

    :param rxnvarfile: the Template
    :return:
    """
    explicit_experiments = pd.read_excel(io=rxnvarfile, sheet_name='ManualExps')
    # remove empty rows:
    explicit_experiments = explicit_experiments[~explicit_experiments['Manual Well Number'].isna()]
    # remove unused reagents:
    explicit_experiments = explicit_experiments.ix[:, explicit_experiments.sum() != 0]
    return explicit_experiments.filter(like='Reagent').astype(int)


def get_reagent_number_as_string(reagent_str):
    """Get the number from a string representation"""
    reagent_pat = re.compile('{}(\d+)'.format(REAGENT_ALIAS))
    return reagent_pat.match(reagent_str).group(1)


def abstract_reagent_colnames(df, inplace=True):
    """Replace instances of 'Reagent' with devconfig.REAGENT_ALIAS

    :param df: dataframe to rename
    :return: None or pandas.DataFrame (depending on inplace)
    """
    result = df.rename(columns=lambda x: re.sub('[Rr]eagent', REAGENT_ALIAS, x), inplace=inplace)
    return result
