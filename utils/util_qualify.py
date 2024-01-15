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
import rdflib
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model, Library
from rdflib import Namespace

from utils.logger import CustomLogger

logger = CustomLogger().get_logger()


class BasicValidationInterface:
    """
    This class is used to validate a graph using the Brick basic validation as described here:
    https://github.com/gtfierro/shapes/blob/main/verify.py
    """

    def __init__(self, graph: rdflib.Graph, manifest: str):
        # use the wrapper BrickGraph to initialize the graph
        self.graph = graph
        self.graph.parse(manifest, format='ttl')

    def validate(self) -> None:
        """
        Validate the graph
        :return: print the validation report
        """
        # validate
        valid, report_graph, report = self.graph.validate()
        logger.warning(f"[Brick] Is valid? {valid}")
        if not valid:
            print("-" * 79)
            print(report)
            print("-" * 79)
            raise Exception("Model is invalid")


class BuildingMotifValidationInterface:
    """
    This class is used to validate a graph using the Buildingmotif validation as described here:
    https://github.com/NREL/BuildingMOTIF
    """

    def __init__(self, graph_path: str, manifest_path: str):
        # Define graph path
        self.manifest_path = manifest_path
        self.graph_path = graph_path

    def validate(self) -> None:
        """
        Validate the graph
        :return: print the validation report
        """
        # in-memory instance
        BuildingMOTIF("sqlite://")
        # remind to deactivate logger from BuildingMOTIF class in python package

        # create the namespace for the building
        bldg = Namespace('urn:bldg/')

        # create the building model
        model = Model.create(bldg, description="This is a test model for a simple building")
        # print(model.graph.serialize())

        # load test case model
        model.graph.parse(self.graph_path, format="ttl")
        # print(model.graph.serialize())
        # print(f"Model length {len(model.graph.serialize())}")

        # load brick ontology
        brick = Library.load(ontology_graph="../config/libraries/Brick-subset.ttl")
        # print(f"Model + brick length {len(model.graph.serialize())}")

        # load libraries included with the python package
        constraints = Library.load(ontology_graph="../../buildingmotif/libraries/constraints/constraints.ttl")
        # load libraries excluded from the python package (available from the repository)
        # load manifest into BuildingMOTIF as its own library!
        manifest = Library.load(ontology_graph=self.manifest_path)

        # gather shape collections into a list for ease of use
        shape_collections = [
            brick.get_shape_collection(),
            constraints.get_shape_collection(),
            manifest.get_shape_collection(),
        ]

        # pass a list of shape collections to .validate()
        validation_result = model.validate(shape_collections)
        # print validation result
        logger.warning(f"[BuildingMOTIF] Model <{self.graph_path}> is valid? {validation_result.valid}")

        # if not valid print the validation results
        if not validation_result.valid:
            print("-" * 79)  # just a separator for better error display
            print(validation_result.report_string)
            print("-" * 79)  # just a separator for better error display
            print("Model is invalid for these reasons:")
            for diff in validation_result.diffset:
                print(f" - {diff.reason()}")

            raise Exception("Model is invalid")
