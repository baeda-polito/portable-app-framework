"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2023
Email:        roberto.chiosa@polito.it

Created:      27/09/23
Script Name:  main_qualify.py
Path:         src

Script Description:


Notes:
"""

import os

from utils.util_qualify import BuildingMotifValidationInterface, BasicValidationInterface

if __name__ == '__main__':

    advanced = True

    if advanced:
        BMI = BuildingMotifValidationInterface(
            graph_path=os.path.join("..", "data", "AHU_EXAMPLE", "example_model.ttl"),
            manifest_path=os.path.join("..", "config", "manifest", "example_shape.ttl"),
        )
        BMI.validate()
    else:
        BVI = BasicValidationInterface(
            graph_path=os.path.join("..", "data", "AHU_EXAMPLE", "example_model.ttl"),
            manifest_path=os.path.join("..", "config", "manifest", "example_shape.ttl"),
        )
        # BVI.describe()
        BVI.validate()
