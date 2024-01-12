"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2024
Email:        roberto.chiosa@pinvision.it

Created:      12/01/24
Script Name:  create_new_app.py
Path:         src

Script Description: Util to create new app


Notes:
"""
import os
import sys

if __name__ == '__main__':
    """
    Create a new application folder.
    :param app_name:
    """
    app_name = sys.argv[1]
    os.mkdir(app_name)
    # create file
    with open(os.path.join(app_name, 'config.yaml'), 'w') as f:
        f.write(f"""details:
  name: Check Variables
  description: Checks if a certain AHU has the required variables
  version: 1.0
  author: Roberto Chiosa
  email: roberto.chiosa@polito.it
  created_at: 2024-01-01
        """)
    with open(os.path.join(app_name, 'query.rq'), 'w') as f:
        f.write("""SELECT ?point ?component ?type WHERE {
    ?point rdf:type ?type .
    ?component brick:hasPoint ?point .
}""")

    with open(os.path.join(app_name, 'manifest.ttl'), 'w') as f:
        f.write("""@prefix brick:      <https://brickschema.org/schema/Brick#> .
@prefix owl:        <http://www.w3.org/2002/07/owl#> .
@prefix sh:         <http://www.w3.org/ns/shacl#> .
@prefix constraint: <https://nrel.gov/BuildingMOTIF/constraints#> .
@prefix :           <urn:my_site_constraints/> .

:
    a owl:Ontology .
           """)
