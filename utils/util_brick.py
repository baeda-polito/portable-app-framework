# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@pinvision.it
#
# Created:      27/09/23
# Script Name:  util_brick.py
# Path:         utils
#
# Script Description:
#
#
# Notes:

import brickschema
import pandas as pd
from rdflib import URIRef, Variable


def parse_results(results, full_uri=False, df=True, no_prefix=False):
    m = {
        'https://brickschema.org/schema/Brick': 'brick',
        'http://www.w3.org/1999/02/22-rdf-syntax-ns': 'rdf',
        'http://www.w3.org/2000/01/rdf-schema': 'rdfs',
        'https://brickschema.org/schema/1.0.1/BrickFrame': 'bf',
        'http://www.w3.org/2002/07/owl': 'owl',
        'http://www.w3.org/2004/02/skos/core': 'skos',
        'http://bldg-59': 'bldg',
    }
    """
    alternative
    for row in res:
    print(row)
    if explicit:
        y = [[str(term.split('//')[1]) for term in row] for row in res]
    else:
        y = [[str(term.split('#')[1]) for term in row] for row in res]
    y = list([str(row[0]).split('#')[1] for row in results])
    return y
    """

    if not full_uri:
        rows = [
            [m[r.split('#')[0]] + ':' + r.split('#')[1] if isinstance(r, URIRef) and '#' in r else r for r in
             row] for row in results]

        if no_prefix is True:
            # split prefix from name in list comprehension
            out = [[item.split(':')[1] if isinstance(item, str) and ':' in item else item for item in row] for row in
                   rows]

        else:
            out = rows

    else:
        out = list(results)

    if df:
        out = pd.DataFrame.from_records(
            data=out, columns=[str(item) for item in results.vars if isinstance(item, Variable)])

    return out


class BrickGraph(object):
    """
    High-level interface for interacting with Brick graphs using rdflib
    """

    def __init__(self, load: str = None):
        """
        Different way to load brick in graph
            1) Load from package:             Graph(load_brick_nightly=True) -> getting occasional URL errors for this.
            4) Load from package and file:    Graph(load_brick_nightly=True).serialize('Brick_nightly.ttl', format='ttl')
            2) Load from local file:          Graph().load_file('../data/libraries/Brick-nightly.ttl')
            3) Load from local file:          Graph().parse('../data/libraries/Brick-nightly.ttl', format='ttl')
            4) Load from online:              Graph().parse("https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl", format="ttl")
        """
        if load == "nightly":
            # load nightly version
            self.graph = brickschema.Graph(load_brick_nightly=True).serialize('../data/libraries/Brick-nightly.ttl',
                                                                              format='ttl')
        elif load == "latest":
            # load latest stable version
            self.graph = brickschema.Graph(load_brick=True)
        else:
            # empty graph
            self.graph = brickschema.Graph()

        # todo: expand to have all the relations
        # self.graph.expand(profile="owlrl+shacl+vbis+shacl")

    def query(self, query_string: str):
        """
        Query the graph
        :param query_string: The sparql query encoded as string
        :return: the query result in the graph object
        """
        return self.graph.query(query_string)

    def load_file(self, file_path: str):
        """
        Load a file into the graph
        :param file_path: the path to the file
        :return: Load the file into the graph object
        """
        return self.graph.load_file(file_path, format='ttl')

    def parse(self, file_path: str):
        """
        Parse a file into the graph. Equivalent to load_file
        :param file_path: the path to the file
        :return: Load the file into the graph object
        """
        return self.graph.parse(file_path, format='ttl')

    def describe(self) -> None:
        """
        Describe the graph
        :return: print the graph description
        """
        # count the number of triples
        print(f"Number of triples: {len(self.graph)}")

        q = """
                   PREFIX brick: <https://brickschema.org/schema/Brick#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    select ?component ?bldg_component where {
                                ?bldg_component rdf:type/rdfs:subClassOf* brick:Equipment .
                                ?bldg_component a ?component .
                            }
                """
        res = self.graph.query(q)

        df = pd.DataFrame(res.bindings)
        df.columns = df.columns.map(lambda x: x.strip())
        # group by 'point' and count occurrences
        df_count = df.groupby('component').size().reset_index(name='count')
        # preprocess
        df_count = df_count.sort_values('count', ascending=False)
        # remove from column component string
        df_count['component'] = df_count['component'].map(lambda x: x.split('#')[-1])
        # print result
        print(df_count.to_markdown(index=False))

        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                    select  ?point where {
                        ?bldg_point rdf:type/rdfs:subClassOf* brick:Point .
                        ?bldg_point a ?point . 
                    }

                """
        res = self.graph.query(q)

        df = pd.DataFrame(res.bindings)
        df.columns = df.columns.map(lambda x: x.strip())
        # group by 'point' and count occurrences
        df_count = df.groupby('point').size().reset_index(name='count')
        # preprocess
        df_count = df_count.sort_values('count', ascending=False)
        # remove from column component string
        df_count['point'] = df_count['point'].map(lambda x: x.split('#')[-1])
        # print result
        print(df_count.to_markdown(index=False))
