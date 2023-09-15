# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@polito.it
#
# Created:      15/09/23
# Script Name:  util_check.py
# Path:         utils
#
# Script Description:
#
#
# Notes:
import numpy as np

from utils.logger import CustomLogger
from utils.util_plot import plot_damper, plot_valves
from utils.util_preprocessing import check_low_variance

logger = CustomLogger().get_logger()

plot_flag = False


def check_log_result(result: bool, check_name: str, n: int, message: ''):
    """
    Log the result of a check
    :param message: extra string detailing log
    :param result: boolean representing the result
    :param check_name: the name of the check
    :param n: the number of the check passed to be updated
    """
    if result is True:
        logger.info(f'{check_name} = True ✅ ' + message)
        n += 1
    elif result is None:
        logger.warning(f'{check_name} = None ⚠️ ' + message)
    elif result is False:
        logger.error(f'{check_name} = False ❌ ' + message)
    else:
        raise Exception('The result of the check is not a boolean')

    return n


def check_variables(df):
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

    available_variables = df.columns
    # todo depending on the available variables you can do some checks
    if not all([var in available_variables for var in required_variables]):
        # the variable check has passed we can log and proceed
        # get the difference from the required variables+
        missing_variables = set(required_variables) - set(available_variables)
        raise Exception(
            f'Missing variables in the dataset we suggest to measure the missing values: {list(missing_variables)}')

    else:
        return True, ''


def check_sensor(df, configuration):
    """
    Check if the sensors are stuck
    :param df: the dataset containing the measured variables
    :param configuration: a dictionary of thresholds
    """
    stuck_var = []
    for col in ['sat_col', 'oat_col', 'rat_col', 'mat_col']:
        try:
            stuck = True if check_low_variance(df, col, configuration["sensor_variance_threshold"]) else False
            stuck_var.append(col) if stuck else None
        except KeyError:
            pass

    if stuck_var.__len__() > 0:
        return False, f'(check the sensors {list(stuck_var)})'
    else:
        return True, ''


def check_min_oa(df, configuration):
    """
    Check if the minimum outdoor air is respected.
    Is the minimum outdoor-air damper position reasonable (between 10% and 20%)?
    NB trim under 50% and find median
    
    :param df: the dataset containing the measured variables
    :param configuration: a dictionary of thresholds
    """

    if df.shape[0] == 0:
        logger.info('check_min_oa_passed = None (Not enough data)')
    else:
        damper_min = df['oa_dmpr_sig_col'][df['oa_dmpr_sig_col'] < 0.4].median()

        if damper_min > configuration['damper_min_oa_threshold']:
            return False, f'(damper_min = {round(damper_min, 3)}) - Verify the minimum ventilation'
        else:
            return True, f'(damper_min = {round(damper_min, 3)})'


def check_damper(df, configuration, plot_flg=False):
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
            return False, f'(oaf_oa_dmpr_diff = {round(oaf_oa_dmpr_diff, 3)}>' \
                          f'{configuration["diff_damper_oaf_threshold"]}) ' \
                          f'OAF deviates too much from damper position signal)'
        else:
            return True, f'(oaf_oa_dmpr_diff = {round(oaf_oa_dmpr_diff, 3)}<' \
                         f'{configuration["diff_damper_oaf_threshold"]})'

    else:
        return False, f'(Not enough info)'


def check_hc(df):
    """
    Check if there is contemporary heating and cooling
    :param df:
    """
    if not df.empty:
        return False, f'(Possible Contemporary heating and cooling)'
    else:
        return True, ''


def check_valves(df, df_eco, configuration, plot_flg=False):
    """
    Check if the v
    :param plot_flg: whether to plot or not
    :param df: dataset with variables
    :param df_eco: dataset in economizer mode
    :param configuration: dictionary of thresholds
    """
    if not df.empty and not df_eco.empty:

        if plot_flg:
            plot_valves(df, configuration)
        # 2) Does the cooling coil operate when the outdoor-air temperature is lower
        # than the discharge- air temperature set point?
        cooling_coil_median_eco = df_eco[['cooling_sig_col']].median().values[0]
        if cooling_coil_median_eco > configuration["valves_cutoff"]:
            return False, f'(cooling_coil_median_eco = {round(cooling_coil_median_eco, 3)}) ' \
                          f'cooling coil is modulating in eco mode)'

        else:
            return True, ''

    else:
        return None, f'(Not enough info)'
