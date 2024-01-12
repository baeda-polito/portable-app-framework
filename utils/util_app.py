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
import os

from utils.logger import CustomLogger
from utils.util import load_file


class ApplicationData:
    """
    Application data class
    """

    def __init__(self, data=None, metadata=None):
        # The graph_path and datasource are external to the configuration file.
        self.data = data
        self.metadata = metadata
        self.result = None
        self.message = 'No message'


class Application:
    """
    Application class
    """

    def __init__(self, data=None, metadata=None, config_folder=None):
        # Class specific logger
        self.logger = CustomLogger().get_logger()
        # The graph_path and datasource are external to the configuration file.
        self.data = data
        self.metadata = metadata
        self.res = None
        # The config folder should contain
        # - config.yaml
        # - manifest.yaml
        # - query.ttl

        if os.path.join(config_folder, 'config.yaml') is None:
            raise FileNotFoundError('config.yaml not found')
        elif os.path.join(config_folder, 'manifest.yaml') is None:
            raise FileNotFoundError('manifest.yaml not found')
        elif os.path.join(config_folder, 'query.ttl') is None:
            raise FileNotFoundError('query.ttl not found')
        else:
            config_file = load_file(os.path.join(config_folder, 'config.yaml'), yaml_type=True)
            self.details = config_file['details']
            self.analyze_functions = config_file['analyze_functions']
            self.manifest = load_file(os.path.join(config_folder, 'manifest.ttl'))
            self.query = load_file(os.path.join(config_folder, 'query.rq'))

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
        pass

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
        # todo fetch metadata grom provided graph
        fetch_metadata = {
            'satsp_col': 'satsp_col',
            'sat_col': 'sat_col',
            'oat_col': 'oat_col',
            'rat_col': 'rat_col',
            'cooling_sig_col': 'cooling_sig_col',
            'heating_sig_col': 'heating_sig_col',
            'oa_dmpr_sig_col': 'oa_dmpr_sig_col'
        }
        # todo fetch data from provided data by filtering
        # get columns with metadata matching df_fetch_metadata
        fetch_data = self.data.loc[:, self.data.columns.isin(fetch_metadata.keys())]

        self.res = ApplicationData(data=fetch_data, metadata=fetch_metadata)
