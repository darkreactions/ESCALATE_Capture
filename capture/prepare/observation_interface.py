from utils.data_handling import build_experiment_names_df, update_sheet_column
from utils import globals
import capture.devconfig as config
from capture.prepare.experiment_interface import MakeWellList, MakeWellList_WF3, MakeWellList_WF3_small
from utils.globals import lab_safeget

def upload_observation_interface_data(rxndict, vardict, gc, interface_uid):
    """

    :param gc:
    :param interface_uid:
    :return:
    """

    sheet = gc.open_by_key(interface_uid).sheet1

    # todo: only build this once: we now read the manual spec sheet three times...
    experiment_names = build_experiment_names_df(rxndict, vardict)
#    experiment_index = range(1, len(experiment_names) + 1)
    total_exp_entries = int(rxndict['wellcount'])
    #TODO: organize code around workflow handling... at this moment moving to specify level seems appropriate
    # Maybe setting the variables for actions in dictionaries that can be created through some interface
    # TODO: This needs to be moved to a dict in the devconfig with clear configuration standards
    uploadlist = []
    if rxndict['ExpWorkflowVer'] >= 3 and rxndict['ExpWorkflowVer'] < 4:
        uploadtarget = sheet.range(f'A2:D{total_exp_entries+1}')

        df = MakeWellList_WF3_small("nothing", total_exp_entries)

        exp_counter = list(range(1,total_exp_entries+1)) # +1 to fix off by 1
        wellnamelist = df['Vial Site'].values.tolist()
        letter_list = [x[:1] for x in wellnamelist]
        number_list = [x[1:] for x in wellnamelist]

        count = 0
        while count < len(exp_counter):
            uploadlist.append(exp_counter[count])
            uploadlist.append(letter_list[count])
            uploadlist.append(number_list[count])
            uploadlist.append(wellnamelist[count])
            count += 1

        count = 0
        for cell in uploadtarget:
            try:
                cell.value = uploadlist[count]
                count += 1  
            except:
                count += 1
        sheet.update_cells(uploadtarget)

    else:
        if globals.get_lab() == 'MIT_PVLab':
            uploadtarget = sheet.range(f'A2:A{total_exp_entries+1}')
            df = MakeWellList("nothing", total_exp_entries)

            uploadlist = list(range(1,total_exp_entries+1)) # +1 to fix off by 1

            count = 0
            for cell in uploadtarget:
                try:
                    cell.value = uploadlist[count]
                    count += 1  
                except:
                    count += 1
            sheet.update_cells(uploadtarget)

        else:
            uploadtarget = sheet.range(f'A2:D{total_exp_entries+1}')

            df = MakeWellList("nothing", total_exp_entries)

            exp_counter = list(range(1,total_exp_entries+1)) # +1 to fix off by 1
            wellnamelist = df['Vial Site'].values.tolist()
            letter_list = [x[:1] for x in wellnamelist]
            number_list = [x[1:] for x in wellnamelist]

            count = 0
            while count < len(exp_counter):
                uploadlist.append(exp_counter[count])
                uploadlist.append(letter_list[count])
                uploadlist.append(number_list[count])
                uploadlist.append(wellnamelist[count])
                count += 1

            count = 0
            for cell in uploadtarget:
                try:
                    cell.value = uploadlist[count]
                    count += 1  
                except:
                    count += 1
            sheet.update_cells(uploadtarget)

    obs_columns = lab_safeget(config.lab_vars, globals.get_lab(), 'observation_interface')
    update_sheet_column(sheet, data=experiment_names['Experiment Names'],
                        col_index=obs_columns['uid_col'], start_row=2)
    return


def upload_modelinfo_observation_interface(model_info_df, gc, interface_uid):
    '''push the model information to the observation interface

    :param model_info_df: 2xN data frame with 'modelname' and 'participantname' 
                          as columns and N being the total number of experiments
    :param interface_uid: google sheets observation UID 
    :return: NULL
    '''
    sheet = gc.open_by_key(interface_uid).sheet1

    observation_dict = lab_safeget(config.lab_vars, globals.get_lab(), 'observation_interface')
    modeluid_col = observation_dict['modeluid_col']
    participantuid_col = observation_dict['participantuid_col']

    update_sheet_column(sheet, data=model_info_df['modelname'],
                        col_index=modeluid_col, start_row=2)
    update_sheet_column(sheet, data=model_info_df['participantname'],
                        col_index=participantuid_col, start_row=2)
    return

