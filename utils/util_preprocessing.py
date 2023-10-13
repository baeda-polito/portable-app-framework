# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@polito.it
#
# Created:      24/04/23
# Script Name:  preprocessing.py
# Path:         utils
#
# Script Description:
# This script contains the available preprocessing functions defined in the yaml file.
#
# Notes:
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from utils.logger import CustomLogger
from utils.util_plot import plot_timeseries_transient

logger = CustomLogger().get_logger()


def normalize_01(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Given a dataframe and a column, this function normalizes the column to [0-1].
    :param df: The dataframe to normalize.
    :param col: The column to normalize.
    :return df: The normalized dataframe.
    """
    if df[col].max() > 1:
        df[col] /= 100
        logger.warning(f'Reducing {col} to [0-1]')

    return df


def linear_interpolation(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function performs a linear interpolation on the dataframe.
    :param df: The dataframe to interpolate.
    :return df_interpolated: The interpolated dataframe.
    """

    # are there any na in the dataset?
    if df.isna().sum().sum() > 0:
        logger.warning('Linear interpolating NaN.')
        df_interpolated = df.interpolate(limit_direction='both', limit=5)
    else:
        # logger.info('No NaN values to interpolate.')
        df_interpolated = df

    return df_interpolated


def drop_na(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function cleans the data from NaN values.
    :param df: The dataframe to clean.
    :return df_clean: The cleaned dataframe.
    """

    # are there any na in the dataset?
    if df.isna().sum().sum() > 0:
        # logger.warning('Dropping NaN.')
        df_clean = df.dropna()
    else:
        # logger.info('No NaN values to drop.')
        df_clean = df

    return df_clean


def resample(df: pd.DataFrame, window: str = '15T') -> pd.DataFrame:
    """
    Resamples dataframe to the bigger available frequency of data.
    :param window: The time window in which i want to aggregate raw data
    :param df: The dataframe to resample.
    :return df_resampled: The resampled dataframe.
    """
    # calculate the minimum interval rounded to closer 5 minute
    # median_interval = df.index.to_series().diff().median().round("1min")
    # logger.info(f'Median timestep in dataset: {median_interval}')

    # the aggregation must be higher than the maximum timedelta in the data
    # if max_interval <= pd.Timedelta(window):

    # resample to the bigger available frequency of data
    df_resampled = df.resample(window).mean()
    # logger.warning(f'Resampling data to {window} interval.')

    # else:
    #     raise ValueError('Data have a maximum time delta larger than the provided time window.')
    return df_resampled


def check_low_variance(df: pd.DataFrame, col: str, threshold: float = 0.01) -> bool:
    """
    This function checks if the variance of a column is too low.
    :param threshold:
    :param df: dataframe
    :param col: column to check
    :return: boolean value indicating if the variance is too low
    """
    column_values = df[col]
    unique_values = column_values.unique()
    variance = column_values.var()

    if len(unique_values) == 1:
        # Only one unique value for column so the signal is fixed to certain value -> the variable has low variance
        # logger.info(f"The column '{col}' has only one unique value.")
        return True
    elif variance > threshold:
        # logger.info(f"The column '{col}' has acceptable variance ({variance:.4f}>{threshold}).")
        return False
    else:
        # logger.error(f"Possible sensor freeze/stuck on '{col}' (var {variance:.4f}<{threshold}).")
        return True


# noinspection PyTypeChecker
def preprocess(df, configuration: dict):
    """
    This function preprocesses the dataframe according to the configuration file.
    :param df: the raw dataset
    :param configuration: dictionary of configuration files
    """
    # df['time'] = pd.to_datetime(df['Datetime']).dt.floor(f'{config["aggregation"]}min')
    # df = df.groupby('time').mean().reset_index()
    df = resample(df=df, window=f'{configuration["aggregation"]}T')

    for col in df.columns:
        try:

            if col in ['sat_col', 'oat_col', 'rat_col', 'mat_col']:

                # wandb.configuration.update({'check_sensor_passed': True}, allow_val_change=True)
                # logger.info('check_sensor_passed = True')

                # find outliers
                series = drop_na(df[col])
                # seasonal period assumed to be 1 day nd so adapt to aggregation parameter
                period = int(24 * 60 / configuration['aggregation'])
                stl_result = seasonal_decompose(series, period=period)
                # stl_result.plot().show()
                # get outlier from the residuals
                arr1 = stl_result.resid.dropna()

                # finding the 1st quartile
                q1 = np.quantile(arr1, 0.25)
                # finding the 3rd quartile
                q3 = np.quantile(arr1, 0.75)
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
    return df


def get_steady(df, configuration: dict, plot_flag: bool = False, filename=None):
    """
    This function finds the steady state periods in the dataset.
    :param filename:
    :param df:  the raw dataset
    :param configuration:  dictionary of configuration files
    :param plot_flag: whether to plot the results
    :return:
    """
    df_steady = df.copy()
    # expand resampling to 1 hour expanding on timeseries where no data is available
    # df_steady = df_steady.resample(f'{config["aggregation"]}min', on='time').mean().reset_index()
    slope_cooling = pd.Series(
        np.gradient(df_steady['cooling_sig_col']),
        df_steady.index,
        name='slope_cooling')
    slope_heating = pd.Series(
        np.gradient(df_steady['heating_sig_col']),
        df_steady.index,
        name='slope_heating')
    slope_damper = pd.Series(
        np.gradient(df_steady['oa_dmpr_sig_col']),
        df_steady.index,
        name='slope_damper')

    # join slopes to unique slope series keeping the max value
    slope = pd.concat([slope_cooling, slope_damper, slope_heating], axis=1)
    slope = slope.abs().max(axis=1)
    # concatenate slope to df_damper
    df_steady = pd.concat([df_steady, slope], axis=1)
    df_steady = df_steady.rename(columns={0: 'slope'})

    if plot_flag:
        plot_timeseries_transient(df_steady, configuration, filename)

    # if more than threshold tag
    df_steady['slope'] = np.where(
        df_steady['slope'] > configuration['transient_cutoff'],
        'transient',
        'steady'
    )
    # count steady vs transient
    # perc_steady = df_steady[df_steady['slope'] == 'steady'].shape[0] / df_steady.shape[0]
    # perc_transient = df_steady[df_steady['slope'] == 'transient'].shape[0] / df_steady.shape[0]

    return df_steady
