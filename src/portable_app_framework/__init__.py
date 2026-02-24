import argparse
import importlib
import os
import shutil

import inquirer
import pandas as pd
import yaml

from .utils.logger import logger
from .utils.util import load_file
from .utils.util_brick import parse_raw_query
from .utils.util_qualify import BasicValidationInterface
from .utils.util_qualify import BuildingMotifValidationInterface

# create app folder if not exists
MODULE_BASEPATH = os.path.dirname(__file__)
USER_BASEPATH = os.getcwd()
APP_FOLDER = os.path.join(USER_BASEPATH, 'app')

if not os.path.exists(APP_FOLDER):
    os.makedirs(APP_FOLDER, exist_ok=True)
    logger.info(f'Created app folder in {APP_FOLDER}')


class Application:
    """
    Application class
    """

    def __init__(self, metadata=None, app_name=None, base_path=None):
        # Class specific logger
        self.logger = logger
        # The graph_path and datasource are external to the configuration file.
        self.metadata = metadata
        self.app_name = app_name
        self.res_qualify = None
        self.res_fetch = None
        self.res_preprocess = None
        self.res_analyze = None

        # Resolve the app folder based on provided base_path or default
        if base_path:
            self.app_folder = os.path.join(base_path, 'app')
        else:
            self.app_folder = APP_FOLDER

        self.path_to_app = os.path.join(self.app_folder, app_name)

        '''
        The config folder should be structured as follows
        . <NAME>
        ├── config.yaml
        ├── manifest.ttl
        └── query.rq
        '''

        # Class variable to store available app names
        available_app = os.listdir(self.app_folder)  # Add your app names here
        # get only directories that start with app
        available_app_names = [app for app in available_app if app.startswith('app')]

        # Log if no apps are found in the resolved path
        if not available_app_names:
            self.logger.warning(f'No apps found in {self.app_folder}. Check if the base_path is correct.')

        if app_name not in available_app_names:
            raise ValueError(f"Invalid app name. Available app names: {available_app_names}")

        if not os.path.exists(os.path.join(self.app_folder, app_name, 'config.yaml')):
            raise FileNotFoundError('config.yaml not found')
        elif not os.path.exists(os.path.join(self.app_folder, app_name, 'manifest.ttl')):
            raise FileNotFoundError('manifest.ttl not found')
        elif not os.path.exists(os.path.join(self.app_folder, app_name, 'query.rq')):
            raise FileNotFoundError('query.rq not found')
        else:
            config_file = load_file(os.path.join(self.app_folder, app_name, 'config.yaml'), yaml_type=True)
            self.details = config_file['details']
            self.parameters = config_file['parameters']
            self.manifest = os.path.join(self.app_folder, app_name, 'manifest.ttl')
            self.query = load_file(os.path.join(self.app_folder, app_name, 'query.rq'))

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
                graph=self.metadata
            )
            res_basic_validation = basic_validation.validate()

            building_motif_validation = BuildingMotifValidationInterface(
                graph=self.metadata,
                app_name=self.app_name,
            )
            res_building_motif_validation = building_motif_validation.validate()
            # is at least one of the two validation valid?
            is_valid = all([res_basic_validation, res_building_motif_validation])

        except Exception as e:
            # If some exception the valid is still false
            self.logger.error(f'Error during the validation of the manifest: {e}')

        self.res_qualify = is_valid
        return is_valid

    def fetch(self) -> dict:
        """
        The fetch component performs the retrival of the metadata based on the sparql query.
        This method returns the mapping convention between the internal naming convention (i.e., naming convention
        defined in the SPARQL query) an the external naming convention (i.e., naming convention used in the building)

        :return dict: mapping between internal and external naming convention
        """
        self.logger.debug(f'Fetching metadata based on sparql query')
        # Perform query on rdf graph
        query_results = self.metadata.query(self.query)
        # Convert the query results to the desired JSON format
        int_to_ext = parse_raw_query(query_results)
        # save internal external naming convention to class
        self.res_fetch = int_to_ext
        # return mapping
        return int_to_ext

    def remap(self, data: pd.DataFrame, fetch_map_dict: dict, mode=None) -> pd.DataFrame:
        """
        The internal_external_mapping component performs the actual mapping of the internal data to the external data
        :param data: The dataframe to be mapped
        :param fetch_map_dict: The mapping dictionary with key-value pairs
        :param mode: The mode of the mapping (to_internal or to_external)
        :return: The mapped dataframe
        """

        dict_to_external = fetch_map_dict
        dict_to_internal = {v: k for k, v in fetch_map_dict.items()}

        if mode == "to_external":
            # rename dataframe to external naming convention
            data = data.rename(columns=dict_to_external)
        elif mode == "to_internal":
            # rename dataframe to internal naming convention
            data = data.rename(columns=dict_to_internal)
        else:
            self.logger.error(f'Invalid mode {mode}. Please choose between to_external or to_internal')

        return data

    def preprocess(self, *args, **kwargs):
        """
        The purpose of this component is to perform the actual analysis of the data.
        """
        # Dynamically import the analyze module
        preprocess_module = importlib.import_module(f"app.{self.app_name}.preprocess", package=__name__)

        # Get the function object from the module
        preprocess_fn = getattr(preprocess_module, "preprocess_fn", None)

        if preprocess_fn is not None and callable(preprocess_fn):
            # Call the function with the provided arguments
            self.res_preprocess = preprocess_fn(*args, **kwargs)
            return self.res_preprocess
        else:
            self.logger.error(f"Function {preprocess_fn} not found in analyze module.")
            return None

    def analyze(self, *args, **kwargs):
        """
        The purpose of this component is to perform the actual analysis of the data.
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
            self.logger.error(f"Function {analyze_fn} not found in analyze module.")
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


def cli_list_app():
    """
    List available applications excluding example
    """
    # list folders in app folder inside the module
    app_folder = os.listdir(os.path.join(USER_BASEPATH, APP_FOLDER))  # todo should be set by the user
    # list only folders that start with ap
    app_names = [app for app in app_folder if app.startswith('app')]
    print(app_names)


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
        md += f'- Preprocess function ([preprocess.py](preprocess.py))\n'
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
        md += f'df = pd.DataFrame()# get df according to your logic \n'
        md += f'df_preprocess = app.preprocess(df)\n'
        md += f'final_result = app.analyze(df_preprocess)\n'
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
    if args.command == 'ls':
        cli_list_app()
    else:
        parser.print_help()
