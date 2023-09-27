# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@pinvision.it
#
# Created:      27/09/23
# Script Name:  main_qualify.py
# Path:         src
#
# Script Description:
#
#
# Notes:


import os

from utils.util_qualify import BuildingMotifValidationInterface

if __name__ == '__main__':
    # BVI = BasicValidationInterface(
    #     graph_path=self.graph_path,
    #     manifest_path=manifest_path,
    # )
    # BVI.describe()
    # BVI.validate()

    BMI = BuildingMotifValidationInterface(
        graph_path=os.path.join("..", "data", "SDAHU.ttl"),
        manifest_path=os.path.join("..", "config", "manifest", "SDAHU_FDD.ttl"),
    )
    BMI.validate()
