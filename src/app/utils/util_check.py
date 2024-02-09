"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2023
Email:        roberto.chiosa@polito.it

Created:      15/09/23
Script Name:  util_check.py
Path:         utils

Script Description:


Notes:
"""
import numpy as np
import pandas as pd

from .logger import CustomLogger
from .util_plot import plot_damper, plot_valves, plot_sat_reset
from .util_preprocessing import check_low_variance
from .. import ApplicationData

logger = CustomLogger().get_logger()

plot_flag = False


def check_log_overall_result(result: dict):
    """
    Log the result of a check
    :param result: a list of boolean representing the result
    """
    # transform each bool into an emoji then print
    # true = ✅
    # false = ❌
    # none = ⚠️

    result_emoji = ['✅' if r is True else '❌' if r is False else '⚠️' for r in result.values()]
    logger.info(f'Result: {"".join(result_emoji)}')


def check_log_result(result: bool, check_name: str, message: ''):
    """
    Log the result of a check
    :param message: extra string detailing log
    :param result: boolean representing the result
    :param check_name: the name of the check
    """
    if result is True:
        logger.info(f'{check_name} = PASSED ✅ ' + message)
    elif result is None:
        logger.warning(f'{check_name} = WARNING ⚠️ ' + message)
    elif result is False:
        logger.error(f'{check_name} = FAILED ❌ ' + message)
    else:
        raise Exception('The result of the check is not a boolean')


def check_variables1(app_data: ApplicationData):
    app_data.result = True
    app_data.message = ''
    return app_data


# noinspection PyUnresolvedReferences
def check_variables(df: pd.DataFrame):
    """
    Check if the required variables are present in the dataset
    :param df: the dataframe containing the variables
    """

    required_variables = [
        'satsp_col',
        'sat_col',
        'oat_col',
        'rat_col',
        'cooling_sig_col',
        'heating_sig_col',
        'oa_dmpr_sig_col'
    ]
    # remove if all the column is a zero or nan (workaround)
    df = df.loc[:, (df != 0).any(axis=0)]
    df = df.loc[:, (df != np.nan).any(axis=0)]
    available_variables = df.columns
    # todo depending on the available variables you can do some checks
    if not all([var in available_variables for var in required_variables]):
        # the variable check has passed we can log and proceed
        # get the difference from the required variables+
        missing_variables = set(required_variables) - set(available_variables)
        if 'heating_sig_col' in missing_variables:
            return None, f'(Measure {list(missing_variables)} if possible)'
        else:
            return False, f'(Missing variables {list(missing_variables)})'
    else:
        return True, ''


def check_sensor(app_data: ApplicationData, configuration):
    """
    Check if the sensors are stuck
    :param df: the dataset containing the measured variables
    :param configuration: a dictionary of thresholds
    """
    df = app_data.data
    # drop columns if all na in the column or zero
    df = df.loc[:, (df != 0).any(axis=0)]
    stuck_var = []

    # I want to loop on temperature only if available
    available_temperatures = [var for var in {'sat_col', 'oat_col', 'rat_col', 'mat_col'} if var in df.columns]
    available_control = [var for var in {'cooling_sig_col', 'heating_sig_col', 'oa_dmpr_sig_col'} if
                         var in df.columns]

    for col in available_temperatures:
        try:
            stuck = True if check_low_variance(df, col,
                                               configuration["temperature_sensor_variance_threshold"]) else False
            stuck_var.append(col) if stuck else None
        except KeyError:
            pass
    # control signals check
    for col in available_control:
        try:
            stuck = True if check_low_variance(df, col, configuration["control_sensor_variance_threshold"]) else False
            stuck_var.append(col) if stuck else None
        except KeyError:
            pass

    if stuck_var.__len__() > 0:
        app_data.result = None
        app_data.message = f'(Possible sensor freeze/stuck {list(stuck_var)})'
    else:

        app_data.result = True
        app_data.message = ''

    return app_data


def check_min_oa(df, configuration, plot_flag=True):
    """
    Check if the minimum outdoor air is respected.
    Is the minimum outdoor-air damper position reasonable (between 10% and 20%)?
    NB trim under 50% and find median
    
    :param plot_flag:
    :param df: the dataset containing the measured variables
    :param configuration: a dictionary of thresholds
    """

    df = df[
        (df['oa_dmpr_sig_col'] > configuration["damper_cutoff"])
    ]

    if plot_flag:
        plot_damper(df, configuration, filename=configuration['datasource'])

    if df.shape[0] == 0:
        logger.info('check_min_oa_passed = None (Not enough data)')
    else:
        damper_min = df['oa_dmpr_sig_col'][df['oa_dmpr_sig_col'] < 0.4].median()

        if damper_min > configuration['damper_min_oa_threshold']:
            return False, f'(damper_min = {round(damper_min, 3)}) - Verify the minimum ventilation', damper_min
        else:
            return True, f'(damper_min = {round(damper_min, 3)})', damper_min


def check_freeze_protection(df, damper_min):
    """
    Check if when the outdoor-air damper should be locked out to the minimum position for freeze prevention
    when the outdoor-air temperature is below 40oF, and the outdoor-air dampers should be completely closed
    if the mixed-air temperature becomes lower than 40oF. Given that from the previous check it is possible
    to automatically extract the minimum OA we can check that in such conditions the damper is at minimum or closed

    :param damper_min: the minimum outdoor air damper position
    :param df: the dataset containing the measured variables
    """

    # Gets the median value of the outdoor air damper when the mixed air temperature is below 40oF
    # and the outdoor air damper is not closed
    damper_frozen = df['oa_dmpr_sig_col'][df['oa_dmpr_sig_col'] > 0].median()

    if damper_frozen < damper_min * 1.2:
        return True, f'Damper at minimum or lower ({damper_frozen} <= {round(damper_min, 3)})'
    else:
        return None, f'Freeze protection not activated ({damper_frozen} > {round(damper_min, 3)})'


def check_damper(df, damper_min, configuration, plot_flg=False):
    """
    Check if the damper is stuck
    :param plot_flg: whether to plot or not
    :param df: the dataset containing the measured variables
    :param configuration: a dictionary of thresholds
    """
    if not df.empty:
        # trim the distribution below 50%
        if plot_flg:
            plot_damper(df, configuration)

        # How close is the outdoor-air fraction compared to the outdoor-air damper position signal?
        oaf_oa_dmpr_diff = np.abs(df['oaf'] - df['oa_dmpr_sig_col']).mean()
        if oaf_oa_dmpr_diff > configuration['diff_damper_oaf_threshold']:
            return None, f'(oaf_oa_dmpr_diff = {round(oaf_oa_dmpr_diff, 3)}>' \
                         f'{configuration["diff_damper_oaf_threshold"]}) ' \
                         f'OAF deviates too much from damper position signal)'
        else:
            return True, f'(oaf_oa_dmpr_diff = {round(oaf_oa_dmpr_diff, 3)}<' \
                         f'{configuration["diff_damper_oaf_threshold"]})'

    else:
        return None, f'(Not enough info)'


def check_hc(df):
    """
    Check if there is contemporary heating and cooling
    :param df:
    """
    if not df.empty:
        return None, f'(Possible Contemporary heating and cooling)'
    else:
        return True, ''


def check_valves(df, df_eco, configuration):
    """
    Check if the v
    :param df: dataset with variables
    :param df_eco: dataset in economizer mode
    :param configuration: dictionary of thresholds
    """
    if not df.empty and not df_eco.empty:
        if plot_flag:
            plot_valves(df, configuration)

        # todo review check
        # 2) Does the cooling coil operate when the outdoor-air temperature is lower
        # than the discharge air temperature set point?
        cooling_coil_median_eco = df_eco[['cooling_sig_col']].median().values[0]
        if cooling_coil_median_eco > configuration["valves_cutoff"]:
            return None, f'(cooling_coil_median_eco = {round(cooling_coil_median_eco, 3)}) ' \
                         f'cooling coil is modulating in eco mode)'

        else:
            return True, ''

    else:
        return None, f'(Not enough info)'


def check_sat_reset(df, configuration, plot_flag=False, filename=None):
    """
    Check if the Supply Air Temperature is in a reasonable reset schedule
    :param df: dataset with variables
    :param configuration: dictionary of thresholds
    :param plot_flag: whether to plot or not
    :param filename: the name of the file to save the plot
    """

    df['lower_bound'] = df['oat_col'].apply(lambda x: 17 if x <= -10 else 12 if x >= 10 else -0.25 * x + 14.5)
    df['upper_bound'] = df['oat_col'].apply(lambda x: 22 if x <= -15 else 14 if x >= 20 else -0.24 * x + 18.8)

    df_steady = df[df['slope'] == 'steady']

    if plot_flag:
        plot_sat_reset(df_steady, filename)

    percentage_violation = df_steady[(df_steady['sat_col'] < df_steady['lower_bound']) | (
            df_steady['sat_col'] > df_steady['upper_bound'])].shape[0] / len(df_steady)

    if percentage_violation < configuration['sat_reset_threshold']:
        return True, f"Less than 10% of Supply Air Temperature setpoint reset"
    else:
        return False, f'(sat_reset violations = {round(percentage_violation, 3)} > {configuration["sat_reset_threshold"]})'
