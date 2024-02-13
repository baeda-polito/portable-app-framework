"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2024
Email:        roberto.chiosa@pinvision.it

Created:      12/01/24
Script Name:  util_app.py
Path:         utils

Script Description:


Notes:
"""
import argparse
import os

import inquirer  # noqa
import pandas as pd
import yaml
from rdflib import URIRef, Literal

from .utils.logger import CustomLogger
from .utils.util import load_file
from .utils.util_preprocessing import preprocess, get_steady
from .utils.util_qualify import BasicValidationInterface


class ApplicationData:
    """
    Application data class
    """

    def __init__(self,
                 data: pd.DataFrame = None,
                 data_internal: pd.DataFrame = None,
                 data_clean: pd.DataFrame = None,
                 metadata: dict = None,
                 result: bool = None,
                 message: str = 'No message'
                 ):
        # The graph_path and datasource are external to the configuration file.
        self.data = data
        self.data_internal = data_internal
        self.data_clean = data_clean
        self.metadata = metadata
        self.result = result
        self.message = message


class Application:
    """
    Application class
    """

    def __init__(self, data=None, metadata=None, app_name=None):
        # Class specific logger
        self.logger = CustomLogger().get_logger()
        # The graph_path and datasource are external to the configuration file.
        self.data = data
        self.metadata = metadata
        self.res = ApplicationData()
        self.mapping = None

        '''
        The config folder should be structured as follows
        . <NAME>
        ├── config.yaml
        ├── manifest.ttl
        └── query.rq
        '''

        # Class variable to store available app names
        available_app = os.listdir('app')  # Add your app names here
        # get only directories that start with app
        available_app_names = [app for app in available_app if app.startswith('app')]

        if app_name not in available_app_names:
            raise ValueError(f"Invalid app name. Available app names: {available_app_names}")

        if os.path.join('app', app_name, 'config.yaml') is None:
            raise FileNotFoundError('config.yaml not found')
        elif os.path.join('app', app_name, 'manifest.yaml') is None:
            raise FileNotFoundError('manifest.yaml not found')
        elif os.path.join('app', app_name, 'query.ttl') is None:
            raise FileNotFoundError('query.ttl not found')
        else:
            config_file = load_file(os.path.join('app', app_name, 'config.yaml'), yaml_type=True)
            self.details = config_file['details']
            self.manifest = os.path.join('app', app_name, 'manifest.ttl')
            self.query = load_file(os.path.join('app', app_name, 'query.rq'))

    def qualify(self) -> None:
        """
        The "qualify" component defines the metadata and data requirements of an application.

        Mortar evaluates these requirements against all available buildings in order to determine the subset of
        buildings against which the application can run (the execution set).

        Specifically, the qualify component checks
        (1) constraints on building typology and other properties, such as the number of floors in a building, floor area, climate, and occupancy class
        (2) data context constraints, such as the kinds of equipment in the building and available relationships
        (3) data availability constraints, including the amount of historical data and available data resolution

        Notes: https://github.com/flaand/demand_response_controls_library/blob/flaand-dev/examples/boptest/BOPTest_interface_zone_temp_shift_shed_price.py

        """

        try:
            self.logger.debug(f'Validating the ttl file on manifest.ttl')
            basic_validation = BasicValidationInterface(
                graph=self.metadata,
                manifest=self.manifest,
            )
            basic_validation.validate()

            # BMI = BuildingMotifValidationInterface(
            #     graph_path=self.graph_path,
            #     manifest_path=manifest_path,
            # )
            # BMI.validate()
            # TODO inserire qualify su aggregazione e time span
        except Exception as e:
            self.logger.error(f'Error during the validation of the manifest: {e}')

    def fetch(self):
        """
        The fetch component performs the actual retrieval of data from the timeseries database corresponding to the set of streams identified by the Brick queries.

        The data retrieval request uses the following parameters:
        (1) “variable” definitions: these map a name to a Brick query defining the context for a point and the desired
            engineering units for that point (if known), and aggregation function (min,max,mean,count, or raw).
        (2) temporal parameters: defines the bounds on the data, desired resolution, and if we want aligned timestamps.

        The output of the fetch component is an object providing access to the results of the Brick queries, the resulting
        timeseries dataframes, and convenience methods for relating specific dataframes based on the Brick context
        (for example, the setpoint timeseries related to a given sensor timeseries).

        :return: The data
        """
        self.logger.debug(f'Fetching metadata based on sparql query')
        # Perform query on rdf graph
        query_results = self.metadata.query(self.query)
        # todo errore nel renaming variblili

        # todo considerare di spostare tutto in brick utility
        # Convert the query results to the desired JSON format
        head_vars = [str(var) for var in query_results.vars]
        # Convert FrozenBindings to JSON format
        bindings_list = []
        for binding in query_results.bindings:
            binding_dict = {}
            for var in head_vars:
                try:
                    value = binding[var]
                    value_dict = {
                        'type': 'uri' if isinstance(value, URIRef) else 'literal' if isinstance(value,
                                                                                                Literal) else None,
                        'value': str(value),
                    }
                    binding_dict[var] = value_dict
                except KeyError:
                    pass
            bindings_list.append(binding_dict)

        json_results = {
            'head': {'vars': head_vars},
            'results': {'bindings': bindings_list}
        }

        # From the result i need to fetch the corresponding column in data
        fetch_metadata = {}
        for item in json_results['results']['bindings'][0].items():
            fetch_metadata[item[0]] = item[1]['value'].split('#')[1]

        fetch_data = self.data.loc[:, self.data.columns.isin(fetch_metadata.values())]
        # todo remove when in production, remap to convention

        # from dict converts from internal naming convention to original naming convention
        fetch_metadata_rev = {v: k for k, v in fetch_metadata.items()}
        fetch_data_internal = fetch_data.rename(columns=fetch_metadata_rev)

        self.res = ApplicationData(data=fetch_data,
                                   data_internal=fetch_data_internal,
                                   metadata=fetch_metadata)
        self.mapping = fetch_metadata

    def clean(self, fn, *args, **kwargs):
        """
         The purpose of this component is to normalize the timeseries data for the "analyze" component.

       Common operations in the clean component are hole filling,specialized aggregation, and data filtering.
       It is kept modular to facilitate the re-use of standard
       cleaning steps. Application developers can build their own cleaning components or leverage existing methods

       :param fn: function to clean the data
       :return: The cleaned data
        """
        self.res = fn(*args, **kwargs)

    def analyze(self, fn, *args, **kwargs):
        """
        The purpose of this component is to perform the actual analysis of the data.

        The output of the "analyze" component is a set of timeseries dataframes
        containing the results of the analysis. The application developer can choose to save these results to the
        timeseries database, or to perform additional analysis on the results in the aggregate component.

        Updates the res_dict["timeseries"] with the tagged data frame in the column FAULT

        """
        # Call the external function with its arbitrary arguments
        self.res = fn(*args, **kwargs)


def app_name_validation(answers, current):
    if not current.startswith('app_'):
        raise inquirer.errors.ValidationError("", reason="Must start with 'app_'")

    return True


def cli_new_app():
    """
    Create new application from template
    """
    questions = [
        inquirer.Text("name", message="App name?", validate=app_name_validation),
    ]
    answers = inquirer.prompt(questions)
    # copy folder app_example to app_name
    os.system(f'cp -r src/app/template src/app/{answers["name"]}')


def cli_list_app():
    """
    List available applications excluding example
    """
    # list folders in app folder
    app_folder = os.listdir('src/app')
    # list only folders that start with ap
    app_names = [app for app in app_folder if app.startswith('app')]
    print(app_names)


def update_readme(app_name):
    print(f'Updating app {app_name}')
    # read config.yaml and transform in markdown.md
    with open(f'src/app/{app_name}/config.yaml', 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    with open(f'src/app/{app_name}/README.md', 'w') as file:
        md = '[//]: # (AUTOMATICALLY GENERATED DO NOT MODIFY)\n\n'
        md += f'# {data["details"]["name"]}\n'
        md += f'#### Version v.{data["details"]["version"]} ({data["details"]["created_at"]})\n'
        md += f'{data["details"]["description"]}\n\n'
        md += f'The app[^1] is structured as follows:\n'
        md += f'- Configuration file ([config.yaml](config.yaml))\n'
        md += f'- SPARQL query ([query.rq](query.rq))\n'
        md += f'- SHACL Shape or manifest ([manifest.ttl](manifest.ttl))\n\n'
        md += f'[^1]: by {data["details"]["author"]} - {data["details"]["email"]} \n'
        file.write(md)


def cli_update_app():
    """
    Create new application from template
    """

    app_names = [app for app in os.listdir('src/app') if app.startswith('app')]

    questions = [
        inquirer.Checkbox(
            "size",
            message="Which app do you want to update?",
            choices=["all"] + app_names,
        ),
    ]

    answer = inquirer.prompt(questions)

    if len(answer['size']) > 1:
        for app in answer['size']:
            update_readme(app)
    elif answer['size'][0] == 'all':
        for app in app_names:
            update_readme(app)
    else:
        update_readme(answer)


def cli_entry_point():
    """
    Entrypoint for the command line CLI
    """

    parser = argparse.ArgumentParser(description='Utils CLI for the afdd framework.')
    subparser = parser.add_subparsers(dest='command')

    # Command to create a new app from template
    subparser.add_parser('new', help='Create a new application folder from template.')
    # parser_new.add_argument('app_name', help='The name of the application.')

    subparser.add_parser('update', help='Update README of an application.')
    subparser.add_parser('ls', help='List available applications.')

    # Depending on argument does something
    args = parser.parse_args()
    if args.command == 'new':
        cli_new_app()
    if args.command == 'update':
        cli_update_app()
    if args.command == 'ls':
        cli_list_app()
    else:
        parser.print_help()
