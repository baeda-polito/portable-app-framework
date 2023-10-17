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

from apar import APAR01
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
        df = driver_data_fetch(folder, filename)
        print(df.head())

        _fc = APAR01(
            sat_col='sat_col',
            mat_col='mat_col',
            mode=['OM_1_HTG']
        )

        # return a whole new dataframe with fault flag as new col
        df1 = _fc.apply(df)

    # load dataframe
    # apply apar
    # get result
