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
import os
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model, Library
from rdflib import Namespace, Graph
import sqlite3 as lite
import pyshacl
from .logger import logger


class BasicValidationInterface:
    """
    This class is used to validate a graph using the Brick basic validation as described here:
    https://github.com/gtfierro/shapes/blob/main/verify.py
    """

    def __init__(self, graph: Graph):
        # use the wrapper BrickGraph to initialize the graph
        self.graph = graph
        self.graph.parse(os.path.join(os.path.dirname(__file__), "..", "libraries", "Brick-nightly.ttl"), format='ttl')

    def validate(self) -> bool:
        """
        Validate the graph
        :return: print the validation report
        """
        # validate
        valid, results_graph, report = pyshacl.validate(self.graph,
                                                        shacl_graph=self.graph,
                                                        ont_graph=self.graph,
                                                        inference='rdfs',
                                                        abort_on_first=False,
                                                        allow_infos=False,
                                                        allow_warnings=False,
                                                        meta_shacl=False,
                                                        advanced=False,
                                                        js=False,
                                                        debug=False)

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

    def __init__(self, graph: Graph, app_name: str):
        # Define graph path
        self.app_name = app_name
        self.graph = graph

    def validate(self) -> bool:
        """
        Validate the graph
        :return: print the validation report
        """
        # todo dismiss logger buildingmotif
        db_name = "test.db"
        self.clear_db(db_name)
        building_motif = None
        valid = False
        try:
            building_motif = BuildingMOTIF(f"sqlite:///{db_name}")
            building_motif.setup_tables()
            ex = Namespace(f'urn:example#')
            # create the building model
            model = Model.create(ex, description="")
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

        except Exception as e:
            print(f"Error during validation of manifest: {e}")

        finally:
            if building_motif:
                building_motif.close()

        return valid

    @staticmethod
    def clear_db(db_name: str):
        """
        Connect to a dataset and clear all the tables
        :param db_name: db file name
        :return:
        """
        conn = lite.connect(db_name)
        cur = conn.cursor()

        try:
            cur.execute("PRAGMA foreign_keys = OFF;")
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            for table in tables:
                cur.execute(f"DELETE FROM {table[0]};")
            cur.execute("PRAGMA foreign_keys = ON;")
            conn.commit()
        finally:
            conn.close()
