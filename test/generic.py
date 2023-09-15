# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@polito.it
#
# Created:      24/05/23
# Script Name:  generic.py
# Path:         test
#
# Script Description:
#
#
# Notes:

from utils.util import read_json


def test_read_json():
    file = read_json(filename="test/test.json")

    assert file['name'] == "Roberto"
