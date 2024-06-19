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


# from buildingmotif import BuildingMOTIF
# from buildingmotif.dataclasses import Model, Library


class BasicValidationInterface:
    """
    This class is used to validate a graph using the Brick basic validation as described here:
    https://github.com/gtfierro/shapes/blob/main/verify.py
    """

    def __init__(self, graph: brickschema.Graph, manifest: str):
        # use the wrapper BrickGraph to initialize the graph
        self.graph = graph
        self.graph.parse(manifest, format='ttl')

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

# class BuildingMotifValidationInterface:
#     """
#     This class is used to validate a graph using the Buildingmotif validation as described here:
#     https://github.com/NREL/BuildingMOTIF
#     """
#
#     def __init__(self, graph: brickschema.Graph, manifest: str):
#         # Define graph path
#         self.manifest = manifest
#         self.graph = graph
#
#     def validate(self) -> bool:
#         """
#         Validate the graph
#         :return: print the validation report
#         """
#         # todo dismiss logger buildingmotif
#         # in-memory instance
#         BuildingMOTIF("sqlite://")
#         # remind to deactivate logger from BuildingMOTIF class in python package
#
#         # create the namespace for the building
#         bldg = Namespace('urn:bldg/')
#
#         # create the building model
#         model = Model.create(bldg, description="This is a test model for a simple building")
#         # print(model.graph.serialize())
#
#         # load test case model
#         model.add_graph(self.graph)
#         # print(model.graph.serialize())
#         # print(f"Model length {len(model.graph.serialize())}")
#
#         # load brick ontology
#         brick = Library.load(
#             ontology_graph=os.path.join(os.path.dirname(__file__), "..", "libraries", "Brick-subset.ttl"))
#         # print(f"Model + brick length {len(model.graph.serialize())}")
#
#         # load libraries included with the python package
#         constraints = Library.load(
#             ontology_graph=os.path.join(os.path.dirname(__file__), "..", "libraries", "constraints.ttl"))
#         # load libraries excluded from the python package (available from the repository)
#         # load manifest into BuildingMOTIF as its own library!
#         manifest = Library.load(ontology_graph=self.manifest)
#
#         # gather shape collections into a list for ease of use
#         shape_collections = [
#             brick.get_shape_collection(),
#             constraints.get_shape_collection(),
#             manifest.get_shape_collection(),
#         ]
#
#         # pass a list of shape collections to .validate()
#         validation_result = model.validate(shape_collections)
#         valid = validation_result.valid
#
#         # if not valid print the validation results
#         if not validation_result.valid:
#             print("-" * 79)  # just a separator for better error display
#             print(validation_result.report_string)
#             print("-" * 79)  # just a separator for better error display
#             print("Model is invalid for these reasons:")
#             for diff in validation_result.diffset:
#                 print(f" - {diff.reason()}")
#
#             # generated_templates = validation_result.as_templates()
#             # print(generated_templates)
#             # for t in generated_templates:
#             #     print('-' * 80)
#             #     print(t.body.serialize())
#             #     for p in t.parameters:
#             #         ident = input(f"Give value for 'name' of {p} in the above template: ")
#             #         model.add_graph(t.evaluate({"name": BLDG[ident]}))
#             #
#             # print(model.graph.serialize())
#
#         return valid
