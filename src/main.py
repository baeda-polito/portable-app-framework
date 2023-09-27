# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@polito.it
#
# Created:      15/09/23
# Script Name:  main.py
# Path:         src
#
# Script Description:
#
#
# Notes:
import os

from utils.logger import CustomLogger
from utils.util import ensure_dir, list_files
from utils.util_check import check_damper, check_hc, check_log_result, check_min_oa, check_sensor, check_valves, \
    check_variables
from utils.util_driver import driver_data_fetch
from utils.util_plot import plot_damper, plot_valves
from utils.util_preprocessing import get_steady, preprocess

logger = CustomLogger().get_logger()
if __name__ == '__main__':

    FOLDER = os.path.join("..", "data", "LBNL_FDD_Dataset_SDAHU_PQ")
    plot_flag = True
    ensure_dir(FOLDER)

    files = list_files(FOLDER, file_formats=[".csv", ".parquet"])

    for filename in files:
        print('\n')
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
            'sensor_variance_threshold': 0.01,
            'damper_min_oa_threshold': 0.3,
            'diff_damper_oaf_threshold': 0.3
        }

        n = 0  # number of check passed

        # fetch data depending on the folder and filename
        df = driver_data_fetch(FOLDER, filename)

        # VARIABLES CHECK
        df_varcheck = df.dropna(axis=1, how='all')
        result, message = check_variables(df_varcheck)
        n = check_log_result(result, 'check_variables', n, message)

        # STUCK TEMPERATURE SENSOR VARIABLE
        result, message = check_sensor(df, config)
        n = check_log_result(result, 'check_sensor', n, message)

        # PREPROCESSING
        df = preprocess(df, config)

        # HISTOGRAM OF ALL VARIABLES
        # df_hist = df.melt(id_vars='time')
        # plot_histogram(df_hist)

        # IDENTIFY TRANSIENT
        df_steady = get_steady(df, config, plot_flag=plot_flag, filename=datasource)

        # ############  TEMPERATURE BIAS SENSOR ############
        # # scatter plot
        # df_scatter_temp = df_steady.copy()
        # # create hour from time and filter from 6 to 18
        # df_scatter_temp['hour'] = df_scatter_temp['time'].dt.hour
        # df_scatter_temp['day'] = df_scatter_temp['time'].dt.day
        #
        # df_scatter_temp = df_scatter_temp[
        #     (df_scatter_temp['hour'] >= 6) &
        #     (df_scatter_temp['hour'] <= 18) &
        #     (df_scatter_temp['day'] != 7) &
        #     (df_scatter_temp['day'] != 6) &
        #     (df_scatter_temp['slope'] == 'steady') &
        #     (df_steady['oa_dmpr_sig_col'] > config["damper_cutoff"]) &
        #     (df_steady['oa_dmpr_sig_col'] < 1 - config["damper_cutoff"]) &
        #     (df_steady['oat_col'] > 0) &
        #     (df_steady['oat_col'] < 15)
        #     ]
        #
        # # calculate mix - supply
        # df_scatter_temp['sat_mat'] = np.abs(df_scatter_temp['sat_col'] - df_scatter_temp['mat_col'])
        # # df_scatter_temp['rat_mat'] = df_scatter_temp['rat_col'] - df_scatter_temp['mat_col']
        # temp_bias = df_scatter_temp['sat_mat'].mean()
        # wandb.log({'TEMPERATURE BIAS': temp_bias})

        # todo spostare alla fine
        # if temp_bias > config['temperature_error']:
        #     wandb.config.update({'check_bias_passed': False}, allow_val_change=True)
        #     logger.error('check_bias_passed = False')
        #
        # else:
        #     wandb.config.update({'check_bias_passed': True}, allow_val_change=True)
        #     logger.info('check_bias_passed = True')

        #
        # df_scatter_temp = df_scatter_temp.melt(id_vars=['time', 'oat_col'])
        # # remove duplicates
        # df_scatter_temp = df_scatter_temp.drop_duplicates()
        # p = px.scatter(df_scatter_temp, x='oat_col', y='value', color='variable',
        #                hover_data=['time']
        #                )
        # p.add_vrect(x0=0, x1=15, col=1,
        #             annotation_text="economixer temp",
        #             fillcolor="grey", opacity=0.2, line_width=0)
        # p.add_hline(y=0, line_width=2, line_dash="dot", line_color="black", opacity=0.5)
        #
        # p.update_layout(xaxis_title='Outdoor air temperature [°C]',
        #                 yaxis_title='Temperature [°C]',
        #
        #                 legend=dict(
        #                     orientation="h",
        #                     yanchor="bottom",
        #                     y=1.02,
        #                     xanchor="right",
        #                     x=1
        #                 ))
        #
        # p.show()

        # MIN AIR REQUIREMENTS

        df_damper_min = df_steady[
            (df_steady['oa_dmpr_sig_col'] > config["damper_cutoff"])
        ]
        result, message = check_min_oa(df_damper_min, config)
        n = check_log_result(result, 'check_min_oa', n, message)
        if plot_flag:
            plot_damper(df_damper_min, config, filename=datasource)

        ############ FREEZE PROTECTION ############
        # df_damper_frozen = df_steady[
        #     (df_steady['oat_col'] < 4)  # 40F
        # ]
        #
        # damper_frozen = df_steady['oa_dmpr_sig_col'][df_steady['oat_col'] < 4].median()
        #
        # if damper_frozen > config["damper_cutoff"]:
        #     wandb.log({'check_freeze_protection_passed': False})
        #     logger.error(f'check_freeze_protection_passed = False (median damper position = {damper_frozen})')
        # else:
        #     wandb.log({'check_freeze_protection_passed': True})
        #     logger.info(f'check_freeze_protection_passed = True (median damper position = {damper_frozen})')

        # DAMPER CHECK
        df_damper = df_steady[
            (df_steady['cooling_sig_col'] < config["valves_cutoff"]) &
            (df_steady['heating_sig_col'] < config["valves_cutoff"]) &
            (df_steady['oa_dmpr_sig_col'] > config["damper_cutoff"]) &
            (df_steady['oat_col'] < df_steady['rat_col'])
            # when the outdoor-air temperature is less than the return-air
            # temperature and the AHU is in cooling mode, it is favorable to economize.
            ]

        result, message = check_damper(df_damper, config)
        n = check_log_result(result, 'check_damper', n, message)

        # H/C CHECK
        df_hc = df_steady[
            (df_steady['cooling_sig_col'] > config["valves_cutoff"]) &
            (df_steady['heating_sig_col'] > config["valves_cutoff"])
            ]

        result, message = check_hc(df_hc)
        n = check_log_result(result, 'check_hc', n, message)

        # VALVES CHECK

        # plot valves when working
        df_valves = df_steady.melt(
            id_vars=['dt', 'time', 'oat_col', 'slope'],
            value_vars=['cooling_sig_col', 'heating_sig_col']
        )

        df_valves = df_valves[df_valves['value'] > config["valves_cutoff"]]

        df_valves_eco = df_steady[
            (df_steady['oat_col'] < df_steady['satsp_col'])
            # when the outdoor-air temperature is less than the return-air temperature
            # and the AHU is in cooling mode, it is favorable to economize.
        ]

        result, message = check_valves(df_valves, df_valves_eco, config)
        n = check_log_result(result, 'check_valves', n, message)
        if plot_flag:
            plot_valves(df_valves, config, filename=datasource)

        logger.info(f'n = {n} [' + "✅" * n + '❌' * (6 - n) + ']')
