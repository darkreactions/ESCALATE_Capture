from utils.data_handling import build_experiment_names_df, update_sheet_column
from utils import globals
import capture.devconfig as config


def upload_observation_interface_data(rxndict, vardict, gc, interface_uid):
    """

    :param gc:
    :param interface_uid:
    :return:
    """

    sheet = gc.open_by_key(interface_uid).sheet1

    # todo: only build this once: we now read the manual spec sheet three times...
    experiment_names = build_experiment_names_df(rxndict, vardict)
    experiment_index = range(1, len(experiment_names) + 1)
    update_sheet_column(sheet, data=experiment_index,
                        col_index='A', start_row=2)

    uid_col = config.lab_vars[globals.get_lab()]['observation_interface']['uid_col']
    update_sheet_column(sheet, data=experiment_names['Experiment Names'],
                        col_index=uid_col, start_row=2)
    return


def upload_modelinfo_observation_interface(model_info_df, gc, interface_uid):
    '''push the model information to the observation interface

    :param model_info_df: 2xN data frame with 'modelname' and 'participantname' 
                          as columns and N being the total number of experiments
    :param interface_uid: google sheets observation UID 
    :return: NULL
    '''
    sheet = gc.open_by_key(interface_uid).sheet1

    modeluid_col = config.lab_vars[globals.get_lab()]['observation_interface']['modeluid_col']
    participantuid_col = config.lab_vars[globals.get_lab()]['observation_interface']['participantuid_col']

    update_sheet_column(sheet, data=model_info_df['modelname'],
                        col_index=modeluid_col, start_row=2)
    update_sheet_column(sheet, data=model_info_df['participantname'],
                        col_index=participantuid_col, start_row=2)
    return

