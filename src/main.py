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

import numpy as np
import pandas as pd
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose

from utils.logger import CustomLogger
from utils.util import ensure_dir, list_files
from utils.util_driver import driver_data_fetch
from utils.util_preprocessing import check_low_variance, resample, drop_na, normalize_01

logger = CustomLogger().get_logger()
if __name__ == '__main__':

    PROJECT_NAME = "HVAC CHECK"
    # FOLDER = os.path.join("..", "data", "skyspark")
    # FOLDER = os.path.join("..", "data", "SDAHU_parquet_5T")
    FOLDER = os.path.join("..", "data", "MZVAV")
    # FOLDER = os.path.join("..", "data", "mortar_static")

    required_variables = [
        'satsp_col',
        'sat_col',
        'oat_col',
        'rat_col',
        'cooling_sig_col',
        'heating_sig_col',
        'oa_dmpr_sig_col'
    ]

    ensure_dir(FOLDER)
    files = list_files(FOLDER)

    for filename in files:
        # extract information from filename
        datasource = filename.split('.')[0]
        data_format = filename.split('.')[1]

        config = {
            # put here variables needed to group
            'datasource': datasource,
            'aggregation': 15,
            'transient_cutoff': 0.01,
            'valves_cutoff': 0.01,
            'damper_cutoff': 0.0,
            'temperature_error': 1,
            'sensor_variance_threshold': 0.01,
            'damper_min_oa_threshold': 0.3,
            'diff_damper_oaf_threshold': 0.3
        }

        # fetch data depending on the folder and filename
        df = driver_data_fetch(FOLDER, filename)
        check_passed_count = 0
        ############ VARIABLES CHECK ############
        # inderstand whick variables we have
        df_varcheck = df.dropna(axis=1, how='all')
        # update config and logg the variables available
        # wandb.log({'variables_count': df_varcheck.columns.__len__()})
        # wandb.log({'variables': tuple(df_varcheck.columns)})
        available_variables = df_varcheck.columns
        # todo depending on the available variables you can do some checks
        if not all([var in available_variables for var in required_variables]):
            # the variable check has passed we can log and proceed
            # wandb.log({'check_variables_passed': False})
            logger.error('❌ check_variables_passed = False')
            # get the difference from the required variables+
            missing_variables = set(required_variables) - set(available_variables)
            logger.warning(f"Suggest to measure the missing values: {list(missing_variables)}")

        else:
            # the variable check has passed we can log and proceed
            # wandb.log({'check_variables_passed': True})
            logger.info(f'✅ check_variables_passed = True ({list(available_variables)})')
            check_passed_count += 1

            ############ STUCK TEMPERATURE SENSOR VARIABLE ############
            stuck_var = []
            for col in ['sat_col', 'oat_col', 'rat_col', 'mat_col']:
                stuck = False
                try:
                    stuck = True if check_low_variance(df, col, config["sensor_variance_threshold"]) else False
                    stuck_var.append(col) if stuck else None
                except KeyError:
                    pass

            if stuck_var.__len__() > 0:
                # wandb.log({'check_sensor_passed': False})
                logger.error(f'❌ check_sensor_passed = False (check the sensors {list(stuck_var)})')
            else:
                # wandb.log({'check_sensor_passed': True})
                logger.info('✅ check_sensor_passed = True')
                check_passed_count += 1

            ############ PREPROCESSING ############

            # df['time'] = pd.to_datetime(df['Datetime']).dt.floor(f'{config["aggregation"]}min')
            # df = df.groupby('time').mean().reset_index()

            df = resample(df=df, window=f'{config["aggregation"]}T')

            for col in df.columns:
                try:

                    if col in ['sat_col', 'oat_col', 'rat_col', 'mat_col']:

                        # wandb.config.update({'check_sensor_passed': True}, allow_val_change=True)
                        # logger.info('check_sensor_passed = True')

                        # find outliers
                        series = drop_na(df[col])
                        # seasonal period assumed to be 1 day nd so adapt to aggregation parameter
                        period = int(24 * 60 / config['aggregation'])
                        stl_result = seasonal_decompose(series, period=period)
                        # stl_result.plot().show()
                        # get outlier from the residuals
                        arr1 = stl_result.resid.dropna()

                        # finding the 1st quartile
                        q1 = np.quantile(arr1, 0.25)
                        # finding the 3rd quartile
                        q3 = np.quantile(arr1, 0.75)
                        med = np.median(arr1)
                        # finding the iqr region
                        iqr = q3 - q1
                        # finding upper and lower whiskers
                        upper_bound = q3 + (20 * iqr)
                        lower_bound = q1 - (20 * iqr)
                        outliers = arr1[(arr1 <= lower_bound) | (arr1 >= upper_bound)]

                        if 0 < len(outliers) < 20:
                            # limit the number of outliers to first 10 sort
                            outliers = outliers.sort_values(ascending=False).head(10)
                            logger.warning(f'Dropping {len(outliers)} outliers in {col}\n{outliers}')
                            # stl_result.plot().show()
                            df.loc[outliers.index, col] = None

                        # variance = df[col].var()
                        # if variance < 0.01:
                        #     print(f'column {col} has variance {variance} and will be dropped')
                        #     df[col] = None

                    elif col in ['cooling_sig_col', 'heating_sig_col', 'oa_dmpr_sig_col']:
                        # find outliers
                        normalize_01(df, col)
                    else:
                        pass
                except KeyError:
                    pass

            # calculate missing values from available data
            df["oaf"] = (df["rat_col"] - df["sat_col"]) / (df["rat_col"] - df["oat_col"])
            df["oaf"] = np.where(df["oaf"] < 0, None, np.where(df["oaf"] > 1, None, df["oaf"]))

            # calculate optional variables if necessary
            if df["mat_col"].isnull().values.all():
                df["mat_col"] = df["oaf"] * df["oat_col"] + (1 - df["oaf"]) * df["rat_col"]
            df["dt"] = df["sat_col"] - df["mat_col"]
            df['time'] = df.index
            # ############ HISTOGRAM OF ALL VARIABLES ############
            df_hist = df.melt(id_vars='time')
            # if variable in ['satsp_col', 'sat_col', 'oat_col', 'rat_col'] new column temp

            # # plot overall
            p = px.histogram(df_hist, x='value', y='value',
                             color='variable',
                             facet_col='variable',
                             histnorm='probability density',
                             marginal='box',
                             facet_col_wrap=3,
                             )
            p.update_yaxes(matches=None, showticklabels=True)
            # wandb.log({'VARIABLES DISTRIBUTIONS': p})
            p.update_layout(xaxis_title='', yaxis_title='')
            # p.show()
            # p.write_image(f'./img/precheck/TIMESERIES_{filename}.png', width=800, height=1100)

            ############ IDENTIFY TRANSIENT ############
            # identify transient and remove
            df_steady = df.copy()
            # expand resampling to 1 hour expanding on timeseries where no data is available
            # df_steady = df_steady.resample(f'{config["aggregation"]}min', on='time').mean().reset_index()
            slope_cooling = pd.Series(np.gradient(df_steady['cooling_sig_col']), df_steady.index,
                                      name='slope_cooling')
            slope_heating = pd.Series(np.gradient(df_steady['heating_sig_col']), df_steady.index,
                                      name='slope_heating')
            slope_damper = pd.Series(np.gradient(df_steady['oa_dmpr_sig_col']), df_steady.index,
                                     name='slope_damper')

            # join slopes to unique slope series keeping the max value
            slope = pd.concat([slope_cooling, slope_damper, slope_heating], axis=1)
            slope = slope.abs().max(axis=1)
            # concatenate slope to df_damper
            df_steady = pd.concat([df_steady, slope], axis=1)
            df_steady = df_steady.rename(columns={0: 'slope'})

            p = px.bar(df_steady, x='time', y='slope', title='Slope of cooling signal')
            # add cooling signal
            p.add_scatter(x=df_steady['time'], y=df_steady['cooling_sig_col'], name='cooling signal',
                          mode='lines')
            p.add_scatter(x=df_steady['time'], y=df_steady['heating_sig_col'], name='heating signal',
                          mode='lines')
            p.add_scatter(x=df_steady['time'], y=df_steady['oa_dmpr_sig_col'], name='damper signal',
                          mode='lines')
            p.update_layout(xaxis_title='Time',
                            yaxis_title='Value',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ))
            p.add_hrect(y0=0, y1=config["transient_cutoff"], col=1,
                        annotation_text="transient_cutoff", annotation_position="left",
                        fillcolor="grey", opacity=0.5, line_width=0)
            # p.show()
            # wandb.log({'TRANSIENT': p})

            # if more than treshold tag
            df_steady['slope'] = np.where(df_steady['slope'] > config['transient_cutoff'], 'transient',
                                          'steady')
            # count steady vs transient
            perc_steady = df_steady[df_steady['slope'] == 'steady'].shape[0] / df_steady.shape[0]
            perc_transient = df_steady[df_steady['slope'] == 'transient'].shape[0] / df_steady.shape[0]
            # wandb.log({'perc_steady': perc_steady, 'perc_transient': perc_transient})

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

            ############ MIN AIR REQUIREMENTS ############
            # IIs the minimum outdoor-air damper position reasonable (between 10% and 20%)?
            # trim under 50% and find median

            df_damper_min = df_steady[
                (df_steady['oa_dmpr_sig_col'] > config["damper_cutoff"])
            ]
            if df_damper_min.shape[0] == 0:
                logger.info('check_min_oa_passed = None (Not enough data)')
            else:
                damper_min = df_damper_min['oa_dmpr_sig_col'][df_damper_min['oa_dmpr_sig_col'] < 0.4].median()

                if damper_min > config['damper_min_oa_threshold']:
                    # wandb.log({'check_min_oa_passed': False})
                    logger.error(
                        f'❌ check_min_oa_passed = False (damper_min = {round(damper_min, 3)}) - Verify the minimum ventilation')
                else:
                    # wandb.log({'check_min_oa_passed': True})
                    logger.info(f'✅ check_min_oa_passed = True (damper_min = {round(damper_min, 3)})')
                    check_passed_count += 1

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

            ############ DAMPER CHECK ############

            df_damper = df_steady[
                (df_steady['cooling_sig_col'] < config["valves_cutoff"]) &
                (df_steady['heating_sig_col'] < config["valves_cutoff"]) &
                (df_steady['oa_dmpr_sig_col'] > config["damper_cutoff"]) &
                (df_steady['oat_col'] < df_steady['rat_col'])
                # when the outdoor-air temperature is less than the return-air temperature and the AHU is in cooling mode, it is favorable to economize.
                ]

            if not df_damper.empty:

                # How close is the outdoor-air fraction compared to the outdoor-air damper position signal?
                oaf_oa_dmpr_diff = np.abs(df_damper['oaf'] - df_damper['oa_dmpr_sig_col']).mean()
                if oaf_oa_dmpr_diff > config['diff_damper_oaf_threshold']:
                    # wandb.log({'check_damper_passed': False})
                    logger.error(
                        f'❌ check_damper_passed = False (oaf_oa_dmpr_diff = {round(oaf_oa_dmpr_diff, 3)}>{config["diff_damper_oaf_threshold"]}) OAF deviates too much from damper position signal)')
                else:
                    # todo calculate some metric
                    # wandb.log({'check_damper_passed': True})
                    logger.info(
                        f'✅ check_damper_passed = True (oaf_oa_dmpr_diff = {round(oaf_oa_dmpr_diff, 3)}<{config["diff_damper_oaf_threshold"]})')
                    check_passed_count += 1

                # trim the distribution below 50% and find bpeak

                p = px.scatter(df_damper,
                               x='oa_dmpr_sig_col',
                               y='oaf',
                               color='slope',
                               symbol='slope',
                               hover_data=['time', 'oat_col', 'slope'],
                               # marginal_x="histogram", marginal_y="histogram"
                               )
                p.update_layout(xaxis_title='Outdoor air damper control signal',
                                yaxis_title='Outdoor air fraction',
                                xaxis_range=[0, 1],
                                yaxis_range=[0, 1],
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                ))
                p.add_vrect(x0=0, x1=config["damper_cutoff"], col=1,
                            annotation_text="damper_cutoff", annotation_position="top left",
                            fillcolor="grey", opacity=0.5, line_width=0)

                # Add '°C' to x-axis tick labels
                p.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1,
                               spikecolor="black",
                               tickformat='.0%', title_font=dict(size=14),
                               tickfont=dict(size=12, color='black'))
                p.update_yaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1,
                               spikecolor="black",
                               tickformat='.0%', title_font=dict(size=14),
                               tickfont=dict(size=12, color='black'))
                p.update_traces(
                    hovertemplate='%{customdata[0]|%Y %B %d}<br>%{customdata[0]|%A, %H:%M}<br><br>y = %{y:.2f}%<br>x = %{x:.2f}%<br>%{customdata[2]}<br>Outdoor air temperature: %{customdata[1]:.2f}°C')

                # p.show()
                # wandb.log({'DAMPER CHECK': p})
            else:
                logger.warning(f'check_damper_passed = None (Not enough info)')

            ############ H/C CHECK ############
            df_hc = df_steady[
                (df_steady['cooling_sig_col'] > config["valves_cutoff"]) &
                (df_steady['heating_sig_col'] > config["valves_cutoff"])
                ]
            if not df_hc.empty:
                # wandb.log({'check_hc_passed': False})
                logger.error('❌ check_hc_passed = False (Possible Contemporary heating and cooling)')
            else:
                # wandb.log({'check_hc_passed': True})
                logger.info('✅ check_hc_passed = True')
                check_passed_count += 1

            ############ VALVES CHECK ############

            # plot valves when working
            df_valves = df_steady.melt(id_vars=['dt', 'time', 'oat_col', 'slope'],
                                       value_vars=['cooling_sig_col', 'heating_sig_col'])

            df_valves = df_valves[df_valves['value'] > config["valves_cutoff"]]

            df_valves_eco = df_steady[
                (df_steady['oat_col'] < df_steady['satsp_col'])
                # when the outdoor-air temperature is less than the return-air temperature and the AHU is in cooling mode, it is favorable to economize.
            ]

            if not df_valves.empty and not df_valves_eco.empty:

                # 2) Does the cooling coil operate when the outdoor-air temperature is lower than the discharge- air temperature set point?
                cooling_coil_median_eco = df_valves_eco[['cooling_sig_col']].median().values[0]
                if cooling_coil_median_eco > config["valves_cutoff"]:
                    # wandb.log({'check_valves_passed': False})
                    logger.error(
                        f'❌ check_valves_passed = False (cooling_coil_median_eco = {round(cooling_coil_median_eco, 3)}) cooling coil is modulating in eco mode)')

                else:
                    # wandb.log({'check_valves_passed': True})
                    logger.info('✅ check_valves_passed = True')
                    check_passed_count += 1

                p = px.scatter(df_valves,
                               x='value',
                               y='dt',
                               opacity=0.6,
                               color='variable',
                               color_discrete_map={'cooling_sig_col': "#01c5f4",
                                                   'heating_sig_col': "#fe7201"},
                               symbol='slope',
                               # facet_col='variable',
                               hover_data=['time', 'oat_col', 'slope'],
                               # marginal_x="histogram", marginal_y="histogram"
                               )
                p.add_vrect(x0=0, x1=config["valves_cutoff"], col=1,
                            annotation_text="valves_cutoff", annotation_position="bottom left",
                            fillcolor="grey", opacity=0.5, line_width=0)
                p.add_hline(y=0, line_width=2, line_dash="dot", line_color="black", opacity=0.5)

                p.update_layout(xaxis_title='Valve control signal', yaxis_title='DT across coil',
                                xaxis_range=[0, 1], yaxis_range=[-20, 20],
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                )
                                )
                p.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across",
                               spikethickness=1,
                               spikecolor="black", tickformat='.0%', title_font=dict(size=14),
                               tickfont=dict(size=12, color='black'))
                p.update_yaxes(showspikes=True, spikesnap="cursor", spikemode="across",
                               spikethickness=1,
                               spikecolor="black", tickformat='°C', title_font=dict(size=14),
                               tickfont=dict(size=12, color='black'))
                p.update_traces(
                    hovertemplate='%{customdata[0]|%Y %B %d}<br>%{customdata[0]|%A, %H:%M}<br><br>y = %{y:.2f}<br>x = %{x:.2f}%<br>%{customdata[2]}<br>Outdoor air temperature: %{customdata[1]:.2f}°C')

                # p.show()
                # p.write_image(f'../results/COOLING_VALVE_{filename}.png', width=600, height=600)
                # wandb.log({'VALVES CHECK': p})
            else:
                logger.error('✅ check_valves_passed = None (Not enough info)')

        logger.info(f'check_passed_count = {check_passed_count} [' + "✅" * check_passed_count + '❌' * (
                8 - check_passed_count) + ']')

        # wandb.log({'check_passed_count': check_passed_count})
        # wandb.finish()
