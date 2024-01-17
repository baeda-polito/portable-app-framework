"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2023
Email:        roberto.chiosa@polito.it

Created:      15/09/23
Script Name:  util_driver.py
Path:         utils

Script Description:


Notes:
"""

import os

import numpy as np
import pandas as pd

from utils.logger import CustomLogger
from utils.util import fahrenheit_to_celsius

logger = CustomLogger().get_logger()


def driver_data_fetch(folder: str, filename: str, full: bool = False) -> pd.DataFrame:
    """
    Converts csv in format to be used in the analysis
    :param folder: the folder name in data folder
    :param filename: the name of the file
    :param full: if True, fan control signal is returned
    :return: the parsed dataframe with the required columns for the analysis
    """
    logger.info(f'Loading {filename}')
    if 'SDAHU' in folder:
        # load data
        df = pd.read_parquet(os.path.join(folder, filename))
        # Select columns and perform data transformations
        df["time"] = df['Datetime']
        # df['heating_sig_col'] = np.zeros(len(df))
        # df['satsp_col'] = fahrenheit_to_celsius(df['SA_TEMPSPT'])
        # df['sat_col'] = fahrenheit_to_celsius(df['SA_TEMP'])
        # df['oat_col'] = fahrenheit_to_celsius(df['OA_TEMP'])
        # df['rat_col'] = fahrenheit_to_celsius(df['RA_TEMP'])
        # df['mat_col'] = fahrenheit_to_celsius(df['MA_TEMP'])
        # df['cooling_sig_col'] = df['CHWC_VLV_DM']
        # df['oa_dmpr_sig_col'] = df['OA_DMPR_DM']

        df['SA_TEMPSPT'] = fahrenheit_to_celsius(df['SA_TEMPSPT'])
        df['SA_TEMP'] = fahrenheit_to_celsius(df['SA_TEMP'])
        df['OA_TEMP'] = fahrenheit_to_celsius(df['OA_TEMP'])
        df['RA_TEMP'] = fahrenheit_to_celsius(df['RA_TEMP'])
        df['MA_TEMP'] = fahrenheit_to_celsius(df['MA_TEMP'])
        df['CHWC_VLV_DM'] = df['CHWC_VLV_DM']
        df['OA_DMPR_DM'] = df['OA_DMPR_DM']

        if full:
            # return fan control signal and system on of status to define OM in APAR application
            df['fan_vfd_speed_col'] = df['SF_SPD']
            df['sys_ctl_col'] = df['SYS_CTL']
            df = df[['time', 'satsp_col', 'sat_col', 'oat_col', 'rat_col', 'cooling_sig_col', 'heating_sig_col',
                     'oa_dmpr_sig_col', 'mat_col', 'fan_vfd_speed_col', 'sys_ctl_col']]
        else:
            # keep only some columns
            # df = df[['time', 'satsp_col', 'sat_col', 'oat_col', 'rat_col', 'cooling_sig_col', 'heating_sig_col',
            #          'oa_dmpr_sig_col', 'mat_col']]

            df = df[['time', 'SA_TEMPSPT', 'SA_TEMP', 'OA_TEMP', 'RA_TEMP', 'MA_TEMP', 'CHWC_VLV_DM', 'OA_DMPR_DM']]


    elif 'DDAHU' in folder:
        # load data
        df = pd.read_parquet(os.path.join(folder, filename))
        # Select columns and perform data transformations
        df["time"] = df['Datetime']
        df['satsp_col'] = fahrenheit_to_celsius(df['RMCLGSPT_E'])
        df['sat_col'] = fahrenheit_to_celsius(df['VAV_DAT_E'])
        df['oat_col'] = fahrenheit_to_celsius(df['OA_TEMP'])
        df['rat_col'] = fahrenheit_to_celsius(df['RA_TEMP'])
        df['mat_col'] = fahrenheit_to_celsius(df['MA_TEMP'])
        df['cooling_sig_col'] = df['CHWC_VLV_DM']
        df['heating_sig_col'] = df['HWC_VLV_DM']
        df['oa_dmpr_sig_col'] = df['OA_DMPR_DM']
        # todo implement full flag
        # keep only some columns
        df = df[['time',
                 'satsp_col',
                 'sat_col',
                 'oat_col',
                 'rat_col',
                 'cooling_sig_col',
                 'heating_sig_col',
                 'oa_dmpr_sig_col',
                 'mat_col']]
    elif 'MZVAV' in folder:
        # load data
        df = pd.read_parquet(os.path.join(folder, filename))
        # Select columns and perform data transformations
        df["time"] = pd.to_datetime(df["Datetime"], format="%m/%d/%Y %H:%M")
        df["AHU: Outdoor Air Temperature"] = pd.to_numeric(df["AHU: Outdoor Air Temperature"])
        df["AHU: Mixed Air Temperature"] = pd.to_numeric(df["AHU: Mixed Air Temperature"])
        df["sat_col"] = fahrenheit_to_celsius(df["AHU: Supply Air Temperature"])
        df["satsp_col"] = fahrenheit_to_celsius(df["AHU: Supply Air Temperature Set Point"])
        df["oat_col"] = fahrenheit_to_celsius(df["AHU: Outdoor Air Temperature"])
        df["rat_col"] = fahrenheit_to_celsius(df["AHU: Return Air Temperature"])
        df["mat_col"] = fahrenheit_to_celsius(df["AHU: Mixed Air Temperature"])
        df["cooling_sig_col"] = df["AHU: Cooling Coil Valve Control Signal"]
        df["heating_sig_col"] = df["AHU: Heating Coil Valve Control Signal"]
        df["oa_dmpr_sig_col"] = df["AHU: Outdoor Air Damper Control Signal  "]
        # todo implement full flag
        # keep only some columns
        df = df[['time', 'satsp_col', 'sat_col', 'oat_col', 'rat_col', 'cooling_sig_col', 'heating_sig_col',
                 'oa_dmpr_sig_col', 'mat_col']]
    elif 'mortar' in folder:
        # load data
        df = pd.read_csv(os.path.join(folder, filename))
        # Select columns and perform data transformations
        df["time"] = pd.to_datetime(df["time"])

        columns_to_convert = ["satsp_col", "sat_col", "oat_col", "rat_col"]

        for col in columns_to_convert:
            try:
                df[col] = fahrenheit_to_celsius(df[col])
            except Exception as e:
                logger.warning(f"Exception {e}")
                pass

        # todo implement full flag

    elif 'skyspark' in folder:
        # load data
        df = pd.read_csv(os.path.join(folder, filename))
        # Select columns and perform data transformations
        df["time"] = pd.to_datetime(df["Timestamp"], format="%Y-%m-%dT%H:%M:%S%z ")
        df['satsp_col'] = fahrenheit_to_celsius(df['33-AHU-3 Supply Air Temperature Setpoint'])
        df['sat_col'] = fahrenheit_to_celsius(df['33-AHU-3 Supply Air Temperature'])
        df['oat_col'] = fahrenheit_to_celsius(df['OA_TEMP'])
        df['rat_col'] = fahrenheit_to_celsius(df['33-AHU-3 Return Air Temperature'])
        df['mat_col'] = fahrenheit_to_celsius(df['33-AHU-3 Mixed Air Temperature'])
        df['cooling_sig_col'] = df['33-AHU-3 Chilled Water Valve Command']
        df['heating_sig_col'] = df['33-AHU-3 Hot Water Valve Command']
        df['oa_dmpr_sig_col'] = df['33-AHU-3 Outside Air Damper Command']
        # keep only some columns
        df = df[['time', 'satsp_col', 'sat_col', 'oat_col', 'rat_col', 'cooling_sig_col', 'heating_sig_col',
                 'oa_dmpr_sig_col', 'mat_col']]
        # todo implement full flag
    elif 'AHU_SX' in folder:
        # load data
        df = pd.read_parquet(os.path.join(folder, filename))
        # Select columns and perform data transformations
        df["time"] = pd.to_datetime(df["Date_hour"], format="%B %d. %Y %I:%M %p")
        df['satsp_col'] = df['Indoor Air Temperature Setpoint']  # already in Celsius
        df['sat_col'] = df['Supply Air Temperature']  # already in Celsius
        df['oat_col'] = df['Outdoor Air Temperature']  # already in Celsius
        df['rat_col'] = df['Return Air Temperature']  # already in Celsius
        df['mat_col'] = np.nan
        df['cooling_sig_col'] = df['Cooling coil water flow request']
        df['heating_sig_col'] = df['Heating coil Water flow request']
        df['oa_dmpr_sig_col'] = df['External Air damper control signal']
        # keep only some columns
        df = df[['time',
                 'satsp_col',
                 'sat_col',
                 'oat_col', 'rat_col', 'cooling_sig_col', 'heating_sig_col',
                 'oa_dmpr_sig_col', 'mat_col']]
        # todo implement full flag
    else:
        raise ValueError('Unknown dataset')

    # ensure that time is parsed iso
    df['time'] = pd.to_datetime(df['time'], utc=True)
    # set date to index dataframe
    df.set_index('time', inplace=True)
    return df
