# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@pinvision.it
#
# Created:      17/10/23
# Script Name:  main_apar.py
# Path:         src
#
# Script Description:
#
#
# Notes:
import os

from apar import *
from utils.logger import CustomLogger
from utils.util import ensure_dir, list_files
from utils.util_driver import driver_data_fetch
from utils.util_preprocessing import resample

if __name__ == '__main__':
    # create logger
    logger = CustomLogger().get_logger()

    folder_name = 'LBNL_FDD_Dataset_SDAHU_PQ'
    folder = os.path.join("..", "data", folder_name)

    # ensure the existence of the folder
    ensure_dir(folder)
    # set plot flag
    plot_flag = False
    # list files in the folder
    files = list_files(folder, file_formats=[".csv", ".parquet"])

    global_result = []
    for filename in files:

        # fetch data depending on the folder and filename
        df_original = driver_data_fetch(folder, filename, full=True)
        df_resampled = resample(df=df_original, window='15T')

        # define operational rules
        _om = APAROperationalModes(
            oa_dmpr_sig_col='oa_dmpr_sig_col',
            oat_col='oat_col',
            heating_sig_col='heating_sig_col',
            cooling_sig_col='cooling_sig_col',
            sys_ctl_col='sys_ctl_col',
            fan_vfd_speed_col='fan_vfd_speed_col',
            si=True
        )

        df_om = _om.apply(df_resampled)
        modes_grouped = _om.print_summary(df_om)

        _rules = {
            # APAR01(sat_col='sat_col', mat_col='mat_col', mode=['OM_1_HTG']),
            # APAR05(satsp_col='satsp_col', oat_col='oat_col', mode=['OM_2_ECO'])
            APAR19(satsp_col='satsp_col', sat_col='sat_col', cooling_sig_col='cooling_sig_col', mode=['OM_4_MIN'],
                   si=True)
        }

        dict_result_single_datasource = {
            'family': folder_name,
            'datasource': filename.split('.')[0],
            **dict(zip(modes_grouped['Operating Mode'], modes_grouped['Time [%]']))
        }

        for _rule in _rules:

            df_rule = _rule.apply(df_om)

            # calculate the percentage of time in a certain operational mode in which the rue is 1
            df_rule_filtered_om = df_rule[df_rule['operating_mode'].isin(_rule.mode)]
            # find how many 1 are there in the rule as percentage
            try:
                percentage_faulty_om = (df_rule_filtered_om[_rule.rule_name].sum() / len(df_rule_filtered_om)) * 100
            except ZeroDivisionError:
                percentage_faulty_om = None

            dict_result_single_datasource[_rule.rule_name] = percentage_faulty_om

        # append result for all apar on single dataframe to overall dataframe
        global_result.append(dict_result_single_datasource)

    # transform to dataframe and save result to data
    df_result = pd.DataFrame(global_result)
    df_result.to_csv(os.path.join('..', 'results', 'result.csv'), index=False)
