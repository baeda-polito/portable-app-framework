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

import pandas as pd

from utils.logger import CustomLogger

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
    median_interval = df.index.to_series().diff().median().round("1min")
    # logger.info(f'Median timestep in dataset: {median_interval}')

    # the aggregation must be higher than the maximum timedelta in the data
    # if max_interval <= pd.Timedelta(window):

    # resample to the bigger available frequency of data
    df_resampled = df.resample(window).mean()
    logger.warning(f'Resampling data to {window} interval.')

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

    if len(unique_values) == 1:
        logger.info(f"The column '{col}' has only one unique value.")

    variance = column_values.var()
    mean = column_values.mean()

    if variance > threshold:
        # logger.info(f"The column '{col}' has acceptable variance ({variance:.4f}>{threshold}).")
        return False
    else:
        logger.error(f"Possible sensor freeze/stuck on '{col}' (var {variance:.4f}<{threshold}).")
        return True
