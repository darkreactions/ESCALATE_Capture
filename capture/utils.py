"""Useful stuff that has no proper home
"""
import pandas as pd


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
