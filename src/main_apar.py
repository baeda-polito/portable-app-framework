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
from utils.util_preprocessing import resample, get_steady

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
        df_resampled = resample(df=df_original, window='5T')
        df_clean = get_steady(df_resampled, {'transient_cutoff': 0.01}, filename=filename)

        # define operational rules
        _om = APAROperationalModes(
            oa_dmpr_sig_col='oa_dmpr_sig_col',
            oat_col='oat_col',
            heating_sig_col='heating_sig_col',
            cooling_sig_col='cooling_sig_col',
            sys_ctl_col='sys_ctl_col',
            fan_vfd_speed_col='fan_vfd_speed_col'
        )

        df_om = _om.apply(df_clean)
        modes_grouped = _om.print_summary(df_om)

        _rules = {
            # Operational Mode 1 - Heating
            # APAR01(sat_col='sat_col', mat_col='mat_col', mode=['OM_1_HTG']),

            # Operational mode 2 - Economizer
            APAR05(oat_col='oat_col', satsp_col='satsp_col', mode=['OM_2_ECO']),
            APAR06(sat_col='sat_col', rat_col='rat_col', mode=['OM_2_ECO']),
            APAR07(sat_col='sat_col', mat_col='mat_col', mode=['OM_2_ECO']),

            # Operational mode 3 - Outdoor air
            APAR08(oat_col='oat_col', satsp_col='satsp_col', mode=['OM_3_OUT']),
            APAR10(oat_col='oat_col', mat_col='mat_col', mode=['OM_3_OUT']),
            APAR11(sat_col='sat_col', mat_col='mat_col', mode=['OM_3_OUT']),
            APAR12(sat_col='sat_col', rat_col='rat_col', mode=['OM_3_OUT']),
            APAR13(cooling_sig_col='cooling_sig_col', sat_col='sat_col', satsp_col='satsp_col', mode=['OM_3_OUT']),
            APAR14(cooling_sig_col='cooling_sig_col', mode=['OM_3_OUT']),

            # Operational mode 4 - Minimum outdoor air
            APAR16(sat_col='sat_col', mat_col='mat_col', mode=['OM_4_MIN']),
            APAR17(sat_col='sat_col', rat_col='rat_col', mode=['OM_4_MIN']),
            APAR19(cooling_sig_col='cooling_sig_col', sat_col='sat_col', satsp_col='satsp_col', mode=['OM_4_MIN']),
            APAR20(cooling_sig_col='cooling_sig_col', mode=['OM_4_MIN']),

            # Operational mode 5 - Unknown

            # Operational mode 0 - All
            APAR25(sat_col='sat_col', satsp_col='satsp_col', mode=['ALL']),
            APAR26(mat_col='mat_col', rat_col='rat_col', oat_col='oat_col', mode=['ALL']),
            APAR27(mat_col='mat_col', rat_col='rat_col', oat_col='oat_col', mode=['ALL'])
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
            if len(df_rule_filtered_om) == 0:
                percentage_faulty_om = None
            else:
                percentage_faulty_om = (df_rule_filtered_om[_rule.rule_name].sum() / len(df_rule_filtered_om)) * 100

            dict_result_single_datasource[_rule.rule_name] = percentage_faulty_om

        # append result for all apar on single dataframe to overall dataframe
        global_result.append(dict_result_single_datasource)

    # transform to dataframe and save result to data
    df_result = pd.DataFrame(global_result)
    # sort columns apar from 01 to 27
    df_result = df_result.reindex(sorted(df_result.columns), axis=1)
    df_result.to_csv(os.path.join('..', 'results', 'result.csv'), index=False)
