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

from apar import APAR01, APAROperationalModes
from utils.logger import CustomLogger
from utils.util import ensure_dir, list_files
from utils.util_driver import driver_data_fetch

if __name__ == '__main__':
    # create logger
    logger = CustomLogger().get_logger()
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
        print(filename)
        # fetch data depending on the folder and filename
        df = driver_data_fetch(folder, filename, full=True)
        # define operational rules
        _om = APAROperationalModes(
            oa_dmpr_sig_col='oa_dmpr_sig_col',
            oat_col='oat_col',
            heating_sig_col='heating_sig_col',
            cooling_sig_col='cooling_sig_col',
            sys_ctl_col='sys_ctl_col',
            fan_vfd_speed_col='fan_vfd_speed_col'
        )

        df1 = _om.apply(df)
        _om.print_summary(df1)

        # apply rule
        df2 = APAR01(sat_col='sat_col', mat_col='mat_col', mode=['OM_1_HTG']).apply(df1)

        # summarize
    # load dataframe
    # apply apar
    # get result
