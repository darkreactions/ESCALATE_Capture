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
