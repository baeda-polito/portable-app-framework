"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2023
Email:        roberto.chiosa@polito.it

Created:      15/09/23
Script Name:  main_precheck.py
Path:         src

Script Description:


Notes:
"""
import os

import pandas as pd

from utils.logger import CustomLogger
from utils.util import ensure_dir, list_files
from utils.util_check import check_damper, check_hc, check_log_result, check_min_oa, check_sensor, check_valves, \
    check_variables, check_log_overall_result, check_freeze_protection
from utils.util_driver import driver_data_fetch
from utils.util_plot import plot_damper, plot_valves
from utils.util_preprocessing import get_steady, preprocess

if __name__ == '__main__':

    # create logger
    logger = CustomLogger().get_logger()
    # define folder with files
    # folder = os.path.join("..", "data", "LBNL_FDD_Dataset_SDAHU_PQ")
    folder = os.path.join("..", "data", "LBNL_FDD_Dataset_SDAHU_PQ")
    # folder = os.path.join("..", "data", "MZVAV_PQ")
    # folder = os.path.join("..", "data", "AHU_SX_PQ")
    # ensure the existence of the folder
    ensure_dir(folder)
    # set plot flag
    plot_flag = False
    # list files in the folder
    files = list_files(folder, file_formats=[".csv", ".parquet"])

    dict_result = {}

    for filename in files:
        print(f'\n########### {filename} ###########')
        # extract information from filename
        datasource = filename.split('.')[0]

        config = {
            # put here variables needed to group
            'datasource': datasource,
            'aggregation': 15,  # minutes
            'transient_cutoff': 0.01,
            'valves_cutoff': 0.01,
            'damper_cutoff': 0.0,
            'temperature_error': 1,
            'temperature_sensor_variance_threshold': 0.01,
            'control_sensor_variance_threshold': 0.01,
            'damper_min_oa_threshold': 0.3,
            'diff_damper_oaf_threshold': 0.3
        }

        n_list = []  # list of check passed
        # fetch data depending on the folder and filename
        df = driver_data_fetch(folder, filename)

        # VARIABLES CHECK
        df_varcheck = df.dropna(axis=1, how='all')
        result, message = check_variables(df_varcheck)
        n_list.append(result)
        check_log_result(result, 'check_variables', message)

        # STUCK TEMPERATURE SENSOR VARIABLE
        result, message = check_sensor(df, config)
        n_list.append(result)
        check_log_result(result, 'check_sensor', message)

        # PREPROCESSING
        df = preprocess(df, config)

        # IDENTIFY TRANSIENT
        df_clean = get_steady(df, config, plot_flag=plot_flag, filename=datasource)

        # MINIMUM OUTDOOR AIR REQUIREMENTS
        df_damper_min = df_clean[
            (df_clean['oa_dmpr_sig_col'] > config["damper_cutoff"])
        ]
        result, message, damper_min = check_min_oa(df_damper_min, config)
        n_list.append(result)
        check_log_result(result, 'check_min_oa', message)
        if plot_flag:
            plot_damper(df_damper_min, config, filename=datasource)

        # FREEZE PROTECTION
        df_freeze = df_clean[
            (df_clean['oat_col'] < 4.4) &
            (df_clean['slope'] == 'steady')
            ]
        result, message = check_freeze_protection(df_freeze, damper_min)
        n_list.append(result)
        check_log_result(result, 'check_freeze_protection', message)

        # DAMPER CHECK
        df_damper = df_clean[
            (df_clean['cooling_sig_col'] < config["valves_cutoff"]) &
            (df_clean['heating_sig_col'] < config["valves_cutoff"]) &
            (df_clean['oa_dmpr_sig_col'] > config["damper_cutoff"]) &
            (df_clean['oat_col'] < df_clean['rat_col'])
            # when the outdoor-air temperature is less than the return-airq
            # temperature and the AHU is in cooling mode, it is favorable to economize.
            ]

        result, message = check_damper(df_damper, config)
        n_list.append(result)
        check_log_result(result, 'check_damper', message)

        # H/C CHECK
        df_hc = df_clean[
            (df_clean['cooling_sig_col'] > config["valves_cutoff"]) &
            (df_clean['heating_sig_col'] > config["valves_cutoff"])
            ]

        result, message = check_hc(df_hc)
        n_list.append(result)
        check_log_result(result, 'check_hc', message)

        # VALVES CHECK
        df_valves = df_clean.melt(
            id_vars=['dt', 'time', 'oat_col', 'slope'],
            value_vars=['cooling_sig_col', 'heating_sig_col']
        )

        df_valves = df_valves[df_valves['value'] > config["valves_cutoff"]]

        df_valves_eco = df_clean[
            (df_clean['oat_col'] < df_clean['satsp_col'])
            # when the outdoor-air temperature is less than the return-air temperature
            # and the AHU is in cooling mode, it is favorable to economize.
        ]

        result, message = check_valves(df_valves, df_valves_eco, config)
        n_list.append(result)
        check_log_result(result, 'check_valves', message)
        if plot_flag:
            plot_valves(df_valves, config, filename=datasource)

        check_log_overall_result(n_list)
        # add row to result dataframe
        dict_result[datasource] = n_list

    df_result = pd.DataFrame.from_dict(dict_result, orient='index')
    print(df_result)
    df_result.to_csv(os.path.join("..", "data", "result.csv"))
