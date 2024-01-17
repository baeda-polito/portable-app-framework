"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2023
Email:        roberto.chiosa@polito.it

Created:      24/02/23
Script Name:  util.py
Path:         utils

Script Description:
This script contains some utility functions used throughout the project.

Notes:
"""

import json
import os
from collections import OrderedDict
from pathlib import Path

import yaml

from utils.logger import CustomLogger

logger = CustomLogger().get_logger()


def load_file(path: str, yaml_type=False):
    """
    Try to load a file given the file path.
    :param path: The path to the file.
    :param yaml_type: If the file is a yaml file.
    :return: The file content.
    """
    try:
        with open(path) as f:
            if yaml_type:
                file = yaml.safe_load(f)
            else:
                file = f.read()
            # logger.info(f'{path} loaded successfully')
    except Exception as e:
        raise e

    return file


def ensure_dir(directory_name: str) -> None:
    """
    Ensure that a directory exists. If it does not, create it.
    :param directory_name: The directory to ensure.
    :return: None
    """
    directory_name = Path(directory_name)
    if not directory_name.is_dir():
        directory_name.mkdir(parents=True)
        # logger.info(f'{directory_name} created successfully')


def list_files(directory_name: str, file_formats=None) -> list:
    """
    Given a folder lists files within matching format
    :param directory_name: The directory that contains the files
    :param file_formats: The file formats to look for
    :return: list of files names
    """
    if file_formats is None:
        file_formats = [".csv", ".parquet"]

    files = [file for file in os.listdir(directory_name) if
             any(file.endswith(file_format) for file_format in file_formats)]

    if len(files) == 0:
        raise Exception("No files found in the specified folder.")
    else:
        return files


def read_json(filename: str):
    """
    Read a JSON file.
    :param filename: The filename to read.
    :return: The JSON data.
    """
    filename = Path(filename)
    with filename.open('rt') as handle:
        return json.load(handle, object_hook=OrderedDict)


def write_json(content, filename: str):
    """
    Write a JSON file.
    :param content: The content to write.
    :param filename: The filename to write.
    :return: None
    """
    filename = Path(filename)
    with filename.open('wt') as handle:
        json.dump(content, handle, indent=4)


def fahrenheit_to_celsius(fahrenheit):
    """
    Converts °F to °C degrees.
    :param fahrenheit: Temperature in °F
    :return: Temperature in °C
    :example:
    >>> fahrenheit_to_celsius(32)
    """
    celsius = (fahrenheit - 32) * (5 / 9)
    return celsius
