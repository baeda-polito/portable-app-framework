"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2023
Email:        roberto.chiosa@polito.it

Created:      27/09/23
Script Name:  util_qualify.py
Path:         utils

Script Description:


Notes:
"""

import brickschema
from .logger import logger
import os
from rdflib import Namespace
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model, Library


class BasicValidationInterface:
    """
    This class is used to validate a graph using the Brick basic validation as described here:
    https://github.com/gtfierro/shapes/blob/main/verify.py
    """

    def __init__(self, graph: brickschema.Graph):
        # use the wrapper BrickGraph to initialize the graph
        self.graph = graph
        self.graph.parse(os.path.join(os.path.dirname(__file__), "..", "libraries", "Brick.ttl"), format='ttl')

    def validate(self) -> bool:
        """
        Validate the graph
        :return: print the validation report
        """
        # validate
        valid, report_graph, report = self.graph.validate()
        logger.debug(f"[Brick] Is valid? {valid}")
        if not valid:
            print("-" * 79)
            print(report)
            print("-" * 79)

        return valid


class BuildingMotifValidationInterface:
    """
    This class is used to validate a graph using the Buildingmotif validation as described here:
    https://github.com/NREL/BuildingMOTIF
    """

    def __init__(self, graph: brickschema.Graph, app_name: str):
        # Define graph path
        self.app_name = app_name
        self.graph = graph

    def validate(self) -> bool:
        """
        Validate the graph
        :return: print the validation report
        """
        # todo dismiss logger buildingmotif
        # in-memory instance
        BuildingMOTIF("sqlite://")
        # create the namespace for the building
        bldg = Namespace('urn:bldg/')
        # create the building model
        model = Model.create(bldg, description="")
        model.add_graph(self.graph)
        manifest = Library.load(ontology_graph=f"app/{self.app_name}/manifest.ttl")
        model.update_manifest(manifest.get_shape_collection())
        validation_result = model.validate()
        valid = validation_result.valid

        # if not valid print the validation results
        if not validation_result.valid:
            print("-" * 79)  # just a separator for better error display
            print(validation_result.report_string)
            print("-" * 79)

        return valid
