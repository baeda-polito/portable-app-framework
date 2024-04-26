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
import importlib
import os
import shutil

import inquirer
import yaml

from .utils.logger import CustomLogger
from .utils.util import load_file
from .utils.util_brick import parse_raw_query
from .utils.util_qualify import BasicValidationInterface, BuildingMotifValidationInterface

# todo spostare all'interno della cli setup
# create app folder if not exists
APP_FOLDER = os.path.join(os.getcwd(), 'app')
os.makedirs(APP_FOLDER, exist_ok=True)
print('App folder created' + APP_FOLDER)

MODULE_BASEPATH = os.path.dirname(__file__)
USER_BASEPATH = os.getcwd()


class Application:
    """
    Application class
    """

    def __init__(self, metadata=None, app_name=None):
        # Class specific logger
        self.logger = CustomLogger().get_logger()
        # The graph_path and datasource are external to the configuration file.
        self.metadata = metadata
        self.app_name = app_name
        self.res_qualify = None
        self.res_fetch = None
        self.res_clean = None
        self.res_analyze = None
        self.path_to_app = os.path.join(USER_BASEPATH, APP_FOLDER, app_name)

        '''
        The config folder should be structured as follows
        . <NAME>
        ├── config.yaml
        ├── manifest.ttl
        └── query.rq
        '''

        # Class variable to store available app names
        available_app = os.listdir(os.path.join(USER_BASEPATH, APP_FOLDER))  # Add your app names here
        # get only directories that start with app
        available_app_names = [app for app in available_app if app.startswith('app')]

        if app_name not in available_app_names:
            raise ValueError(f"Invalid app name. Available app names: {available_app_names}")

        if os.path.join(USER_BASEPATH, APP_FOLDER, app_name, 'config.yaml') is None:
            raise FileNotFoundError('config.yaml not found')
        elif os.path.join(USER_BASEPATH, APP_FOLDER, app_name, 'manifest.yaml') is None:
            raise FileNotFoundError('manifest.yaml not found')
        elif os.path.join(USER_BASEPATH, APP_FOLDER, app_name, 'query.ttl') is None:
            raise FileNotFoundError('query.ttl not found')
        else:
            config_file = load_file(os.path.join(USER_BASEPATH, APP_FOLDER, app_name, 'config.yaml'), yaml_type=True)
            self.details = config_file['details']
            self.parameters = config_file['parameters']
            self.manifest = os.path.join(USER_BASEPATH, APP_FOLDER, app_name, 'manifest.ttl')
            self.query = load_file(os.path.join(USER_BASEPATH, APP_FOLDER, app_name, 'query.rq'))

    def qualify(self) -> bool:
        """
        The "qualify" component defines the metadata and data requirements of an application.

        The metadata requirements are validated in two steps:
        (1) basic validation of the metadata against the Brick schema
        (2) validation of the metadata against the specific constraints through BuildingMOTIF

        The output of the "qualify" component is a boolean value indicating whether the metadata meets the requirements.
        :return: bool indicating whether the requirements are satisfied or not
        """
        self.logger.debug(f'Validating the ttl file on manifest.ttl')
        # by default it is not valid
        is_valid = False
        try:
            basic_validation = BasicValidationInterface(
                graph=self.metadata,
                manifest=self.manifest,
            )
            res_basic_validation = basic_validation.validate()

            building_motif_validation = BuildingMotifValidationInterface(
                graph=self.metadata,
                manifest=self.manifest,
            )
            res_building_motif_validation = building_motif_validation.validate()

            # is at least one of the two validation valid?
            is_valid = any([res_basic_validation, res_building_motif_validation])

        except Exception as e:
            # If some exception the valid is still false
            self.logger.error(f'Error during the validation of the manifest: {e}')

        self.res_qualify = is_valid
        return is_valid

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

        :return:
        """
        self.logger.debug(f'Fetching metadata based on sparql query')
        # Perform query on rdf graph
        query_results = self.metadata.query(self.query)
        # Convert the query results to the desired JSON format
        fetch_metadata = parse_raw_query(query_results)
        # save internal external naming convention to class
        self.res_fetch = fetch_metadata
        # return mapping
        return fetch_metadata

    def internal_external_mapping(self, data):
        """
        The internal_external_mapping component performs the actual mapping of the internal data to the external data
        """
        self.logger.debug(f'Mapping internal data to external data convention')
        # Perform mapping of internal data to external data
        # convert to internal naming convention
        return data

    def clean(self, *args, **kwargs):
        """
        The purpose of this component is to perform the actual analysis of the data.

        The output of the "analyze" component is a set of timeseries dataframes
        containing the results of the analysis. The application saves the data in the form of ApplicationData class.
        """
        # Dynamically import the analyze module
        clean_module = importlib.import_module(f"app.{self.app_name}.clean", package=__name__)

        # Get the function object from the module
        clean_fn = getattr(clean_module, "clean_fn", None)

        if clean_fn is not None and callable(clean_fn):
            # Call the function with the provided arguments
            self.res_clean = clean_fn(*args, **kwargs)
            return self.res_clean
        else:
            print(f"Function {clean_fn} not found in analyze module.")
            return None

    def analyze(self, *args, **kwargs):
        """
        The purpose of this component is to perform the actual analysis of the data.

        The output of the "analyze" component is a set of timeseries dataframes
        containing the results of the analysis. The application saves the data in the form of ApplicationData class.
        """
        # Dynamically import the analyze module
        analyze_module = importlib.import_module(f"app.{self.app_name}.analyze", package=__name__)

        # Get the function object from the module
        analyze_fn = getattr(analyze_module, "analyze_fn", None)

        if analyze_fn is not None and callable(analyze_fn):
            # Call the function with the provided arguments
            self.res_analyze = analyze_fn(*args, **kwargs)
            return self.res_analyze
        else:
            print(f"Function {analyze_fn} not found in analyze module.")
            return None


def app_name_validation(answer, current):
    """
    Validate the app name in the inquirer prompt
    :param answer: The answer
    :param current: The current answer
    :return:
    """
    if not current.startswith('app_'):
        raise inquirer.errors.ValidationError("", reason="Must start with 'app_'")

    return True


def app_folder_validation(answer, current):
    """
    Validate the app name in the inquirer prompt
    :param answer: The answer
    :param current: The current answer
    :return:
    """
    # must be a path in this form /path/to/folder
    if not os.path.exists(current):
        raise inquirer.errors.ValidationError("", reason="Path does not exist")

    return True


def app_selection_validation(answer, current):
    """
    Validate an app is selected
    :param answer: The answer
    :param current: The current answer
    :return:
    """
    # must be a path in this form /path/to/folder
    if len(current) == 0:
        raise inquirer.errors.ValidationError("", reason="Please choose one app from the list")

    return True


def cli_new_app():
    """
    Create new application from template
    """
    questions = [
        inquirer.Text("name", message="App name?", validate=app_name_validation),
    ]
    answer = inquirer.prompt(questions)

    template_folder = os.path.join(MODULE_BASEPATH, "app_template")
    user_folder = os.path.join(USER_BASEPATH, APP_FOLDER, answer["name"])

    # Recursively copy the template folder content to the user folder
    shutil.copytree(template_folder, user_folder, dirs_exist_ok=True)

    # Update the README or perform other necessary actions
    update_readme(answer["name"])


# todo def cli_clone_app():
#     """
#     Create new application from template
#     """
#     app_names = [app for app in os.listdir(os.path.dirname(__file__)) if app.startswith('app')]
#
#     questions = [
#         inquirer.List(
#             "app",
#             message="Which app do you want to clone?",
#             choices=app_names,
#         ),
#     ]
#
#     answer = inquirer.prompt(questions)
#     print(answer)
#     # copy folder app_example to app_name
#     os.system(
#         f'cp -r {os.path.join(MODULE_BASEPATH, answer["app"])} {os.path.join(USER_BASEPATH, APP_FOLDER, answer["app"])}')


# def cli_list_app():
#     """
#     List available applications excluding example
#     """
#     # list folders in app folder inside the module
#     app_folder = os.listdir(MODULE_BASEPATH)
#     # list only folders that start with ap
#     app_names = [app for app in app_folder if app.startswith('app')]
#     print(app_names)


def update_readme(app_name):
    """
    Update the README.md of the app
    :param app_name: The name of the app
    """
    print(f'Updating app {app_name}')
    # read config.yaml and transform in markdown.md
    with open(os.path.join(USER_BASEPATH, APP_FOLDER, app_name, "config.yaml")) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    with open(os.path.join(USER_BASEPATH, APP_FOLDER, app_name, "README.md"), 'w') as file:
        md = '[//]: # (AUTOMATICALLY GENERATED DO NOT MODIFY)\n\n'
        md += f'# {data["details"]["name"]}\n\n'
        md += f'#### Version v.{data["details"]["version"]} ({data["details"]["created_at"]})\n\n'
        md += f'{data["details"]["description"]}\n\n'
        md += f'## Structure\n\n'
        md += f'The app[^1] is structured as follows:\n\n'
        md += f'- Configuration file ([config.yaml](config.yaml))\n'
        md += f'- SPARQL query ([query.rq](query.rq))\n'
        md += f'- SHACL Shape or manifest ([manifest.ttl](manifest.ttl))\n'
        md += f'- Clean function ([clean.py](clean.py))\n'
        md += f'- Analyze function ([analyze.py](analyze.py))\n\n\n'
        md += f'The app accepts the following parameters\n\n'
        for name, value in data["parameters"].items():
            md += f'- `{name}` {value}\n'
        md += f'\n'
        md += f'## Usage\n\n'
        md += f'```python\n'
        md += f'import pandas as pd\n'
        md += f'import brickschema\n'
        md += f'from portable_app_framework import Application\n\n'
        md += f'app = Application(\n'
        md += f'    metadata=brickschema.Graph(),\n'
        md += f'    app_name=\'{app_name}\'\n'
        md += f')\n'
        md += f'qualify_result = app.qualify() # True/False\n'
        md += f'fetch_result = app.fetch() # Dict of mapped variables\n'
        md += f'# get df according to your logic \n'
        md += f'df_clean = app.clean(df)\n'
        md += f'final_result = app.analyze(df_clean)\n'
        md += f'```\n\n'
        md += f'[^1]: by {data["details"]["author"]} - {data["details"]["email"]} \n'
        file.write(md)


def cli_update_app():
    """
    Update the README.md of the app
    """

    app_names = [app for app in os.listdir(os.path.join(USER_BASEPATH, APP_FOLDER)) if app.startswith('app')]

    questions = [
        inquirer.Checkbox(
            name="app",
            message="Which app do you want to update?",
            choices=["all"] + app_names,
            validate=app_selection_validation
        )
    ]

    answer = inquirer.prompt(questions)

    if len(answer['app']) > 1:
        for app in answer['app']:
            update_readme(app)
    elif answer['app'][0] == 'all':
        for app in app_names:
            update_readme(app)
    else:
        update_readme(answer['app'][0])


def cli_entry_point():
    """
    Entrypoint for the command line CLI
    """

    parser = argparse.ArgumentParser(description='Utils CLI for the afdd framework.')
    subparser = parser.add_subparsers(dest='command')

    # Command to create a new app from template
    subparser.add_parser('new', help='Create a new application folder from template.')
    # subparser.add_parser('clone', help='Clone an existing application.') # todo clone da app online
    subparser.add_parser('update', help='Update README of an application.')
    subparser.add_parser('ls', help='List available applications.')

    # Depending on argument does something
    args = parser.parse_args()
    if args.command == 'new':
        cli_new_app()
    # if args.command == 'clone':
    #     cli_clone_app()
    if args.command == 'update':
        cli_update_app()
    # if args.command == 'ls':
    #     cli_list_app()
    else:
        parser.print_help()
