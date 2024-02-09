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
import warnings

import brickschema
import numpy as np
import pandas as pd

from app import Application
from app.utils.logger import CustomLogger
from app.utils.util import ensure_dir, list_files
from app.utils.util_check import check_log_result, check_min_oa, check_sensor, check_freeze_protection, check_damper, \
    check_hc, check_valves, check_sat_reset, check_variables1
from app.utils.util_driver import driver_data_fetch
from app.utils.util_preprocessing import get_steady, preprocess
from src.app.utils.util_plot import plot_histogram, plot_lineplot

warnings.simplefilter(action='ignore', category=FutureWarning)

if __name__ == '__main__':

    # create logger
    logger = CustomLogger().get_logger()

    # define folder with files
    folder = os.path.join("data", "LBNL_FDD_Dataset_SDAHU_PQ")
    # folder = os.path.join("..", "data", "LBNL_FDD_Dataset_SDAHU_PQ")
    # folder = os.path.join("..", "data", "MZVAV_PQ")
    # folder = os.path.join("..", "data", "AHU_SX_PQ")

    # ensure the existence of the folder
    ensure_dir(folder)

    # set plot flag
    plot_flag = False

    # list files in the folder
    files = list_files(folder, file_formats=[".csv", ".parquet"])

    # Define dictionary to collect results
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
            'diff_damper_oaf_threshold': 0.3,
            'sat_reset_threshold': 0.1
        }

        n_list = {}  # list of check passed

        # Get data from driver
        df = driver_data_fetch(folder, filename)
        graph = brickschema.Graph().parse(
            os.path.join("data", "LBNL_FDD_Dataset_SDAHU", "LBNL_FDD_Data_Sets_SDAHU_ttl.ttl"))

        # APP: AHU Variables Check
        app_check_variables = Application(data=df, metadata=graph, app_name='app_check_variables')
        app_check_variables.qualify()
        app_check_variables.fetch()
        app_check_variables.analyze(check_variables1, app_check_variables.res)

        if plot_flag:
            plot_lineplot(app_check_variables.res.data, config['datasource'])
            plot_histogram(app_check_variables.res.data, config['datasource'])
        n_list[app_check_variables.details['name']] = app_check_variables.res.result
        check_log_result(
            result=app_check_variables.res.result,
            check_name=app_check_variables.details['name'],
            message=app_check_variables.res.message
        )

        # APP: Stuck sensor check
        app_check_sensor = Application(data=df, metadata=graph, app_name='app_check_sensor')
        app_check_sensor.qualify()
        app_check_sensor.fetch()
        app_check_sensor.res.result, app_check_sensor.res.message = check_sensor(app_check_sensor.res.data, config)
        n_list[app_check_sensor.details['name']] = app_check_sensor.res.result
        check_log_result(
            result=app_check_sensor.res.result,
            check_name=app_check_sensor.details['name'],
            message=app_check_sensor.res.message
        )

        # PREPROCESSING
        df_clean = preprocess(df, config)
        df_clean = get_steady(df_clean, config, plot_flag=plot_flag, filename=datasource)
        df_clean['heating_sig_col'] = np.zeros(len(df_clean))  # add htg just to avoid error

        # TODO: Aggiungere requirement ON/OFF nel manifest
        # APP: Temperature reset
        app_check_tsat_reset = Application(data=df, metadata=graph, app_name='app_check_tsat_reset')
        app_check_tsat_reset.qualify()
        app_check_tsat_reset.fetch()
        app_check_tsat_reset.res.data = df_clean  # speed up the process instead of fetching again
        app_check_tsat_reset.res.result, app_check_tsat_reset.res.message = check_sat_reset(
            app_check_tsat_reset.res.data,
            config, plot_flag=True, filename=datasource)
        n_list[app_check_tsat_reset.details['name']] = app_check_tsat_reset.res.result
        check_log_result(
            result=app_check_tsat_reset.res.result,
            check_name=app_check_tsat_reset.details['name'],
            message=app_check_tsat_reset.res.message
        )

        # APP: Minimum OA requirement
        app_check_min_oa = Application(data=df, metadata=graph, app_name='app_check_min_oa')
        app_check_min_oa.qualify()
        app_check_min_oa.res.data = df_clean  # speed up the process instead of fetching again
        app_check_min_oa.res.result, app_check_min_oa.res.message, damper_min = check_min_oa(app_check_min_oa.res.data,
                                                                                             config, plot_flag)
        n_list[app_check_min_oa.details['name']] = app_check_min_oa.res.result
        check_log_result(
            result=app_check_min_oa.res.result,
            check_name=app_check_min_oa.details['name'],
            message=app_check_min_oa.res.message
        )

        # APP: Freeze protection check
        app_check_freeze = Application(data=df, metadata=graph, app_name='app_check_freeze')
        app_check_freeze.qualify()
        app_check_freeze.res.data = df_clean[
            (df_clean['oat_col'] < 4.4) &
            (df_clean['slope'] == 'steady')
            ]  # speed up the process instead of fetching again
        app_check_freeze.res.result, app_check_freeze.res.message = check_freeze_protection(app_check_freeze.res.data,
                                                                                            damper_min)
        n_list[app_check_freeze.details['name']] = app_check_freeze.res.result
        check_log_result(
            result=app_check_freeze.res.result,
            check_name=app_check_freeze.details['name'],
            message=app_check_freeze.res.message
        )

        # APP: DAMPER CHECK
        app_check_damper = Application(data=df, metadata=graph, app_name='app_check_damper')
        app_check_damper.qualify()
        app_check_damper.res.data = df_clean[
            (df_clean['cooling_sig_col'] < config["valves_cutoff"]) &
            (df_clean['heating_sig_col'] < config["valves_cutoff"]) &
            (df_clean['oa_dmpr_sig_col'] > config["damper_cutoff"]) &
            (df_clean['oat_col'] < df_clean['rat_col'])
            # when the outdoor-air temperature is less than the return-airq
            # temperature and the AHU is in cooling mode, it is favorable to economize.
            ]
        app_check_damper.res.result, app_check_damper.res.message = check_damper(app_check_damper.res.data,
                                                                                 damper_min,
                                                                                 config)
        n_list[app_check_damper.details['name']] = app_check_damper.res.result
        check_log_result(
            result=app_check_damper.res.result,
            check_name=app_check_damper.details['name'],
            message=app_check_damper.res.message
        )

        # APP: Simultaneous heating and cooling
        app_check_contemporary_hc = Application(data=df, metadata=graph, app_name='app_check_contemporary_hc')
        app_check_contemporary_hc.qualify()
        app_check_contemporary_hc.res.data = df_clean[
            (df_clean['cooling_sig_col'] > config["valves_cutoff"]) &
            (df_clean['heating_sig_col'] > config["valves_cutoff"])
            ]
        app_check_contemporary_hc.res.result, app_check_contemporary_hc.res.message = check_hc(
            app_check_contemporary_hc.res.data)
        n_list[app_check_contemporary_hc.details['name']] = app_check_contemporary_hc.res.result
        check_log_result(
            result=app_check_contemporary_hc.res.result,
            check_name=app_check_contemporary_hc.details['name'],
            message=app_check_contemporary_hc.res.message
        )

        # APP: Delta T check across valves
        app_check_valves = Application(data=df, metadata=graph, app_name='app_check_valves')
        app_check_valves.qualify()

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

        app_check_valves.res.result, app_check_valves.res.message = check_valves(df_valves, df_valves_eco, config)
        n_list[app_check_valves.details['name']] = app_check_valves.res.result
        check_log_result(
            result=app_check_valves.res.result,
            check_name=app_check_valves.details['name'],
            message=app_check_valves.res.message
        )

        # add row to result dataframe
        dict_result[datasource] = n_list

    df_result = pd.DataFrame.from_dict(dict_result, orient='index')
    print(df_result)
    df_result.to_csv(os.path.join("results", "result.csv"))
