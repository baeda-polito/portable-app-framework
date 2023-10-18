from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn
from matplotlib import ticker
from plotly.graph_objs import Figure

from utils.logger import CustomLogger
from utils.util import fahrenheit_to_celsius
from utils.util_preprocessing import check_low_variance, normalize_01

logger = CustomLogger().get_logger()


def exclude_operating_modes(rule_name: str, df: pd.DataFrame, operating_modes: list) -> pd.DataFrame:
    """
    Exclude operating modes from the results of a rule.

    Sets to zero the results of the rule for the operating modes that are not included in the list.
    :param rule_name: Name of the rule
    :param df: Dataframe with the results of the rule
    :param operating_modes: List of operating modes to exclude
    :return: Dataframe with the results of the rule
    """
    # see if columns operating mode exist if not return df
    if 'operating_mode' not in df.columns:
        logger.warning(f"Column 'operating_mode' not found (operating modes not excluded)")
        return df

    if operating_modes == ['ALL']:
        # exclude only mode off
        df[rule_name] = (df[rule_name] * df['operating_mode'] == 'OFF').astype(int).values
    else:
        # exclude results of operating modes that does not apply
        df[rule_name] = df[rule_name] * df['operating_mode'].isin(operating_modes).astype(int).values

    # exclude transient
    # APAR suggest mode swith cdelay of 60 min meaning that we should not consider the first 60 min after mode change
    # In our case we define a windoe of timestamps after each mode change to exclude

    # calculate the minimum interval
    max_interval = df.index.to_series().diff().max().round("5min")
    window_size = timedelta(hours=1) // max_interval

    # Check for inequality with the previous five rows
    result = df['operating_mode'].ne(df['operating_mode'].shift()).rolling(window=window_size).apply(
        lambda x: x.sum() > 0)
    # transform NaN in 0
    result = result.fillna(0)
    # add mode_switch result to dataframe
    df['mode_switch'] = result.astype(int).values
    # if mode_swithc is 1 then set rule to 0 else keep the value
    df[rule_name] = df[rule_name] * (1 - df['mode_switch'])
    logger.warning(f"Excluding detection {window_size} timesteps after each mode change")

    # if any fault warning
    if df[rule_name].sum() > 0:
        logger.warning(f"Faults found for {rule_name}")

        # # summarize by days the number of faults
        # # Get date from index
        # df_faults = df.copy()
        # df_faults['date'] = df_faults.index.date
        # # keep only date and fault tag
        # df_faults = df_faults[['date', rule_name]]
        # # count by date the number of 1
        # df_faults_grouped = df_faults.groupby('date')[rule_name].sum().reset_index()
        # # calculate the time in hours
        # df_faults_grouped[rule_name] *= 5
        # # convert min into timedelta
        # df_faults_grouped[rule_name] = pd.to_timedelta(df_faults_grouped[rule_name], unit='m')
        #
        # # sort by fault descending
        # df_faults_grouped = df_faults_grouped.sort_values(by=rule_name, ascending=False)
        # print(df_faults_grouped.head())
        #
        # # plot variables for the first day
        # df_faults_plot = df.copy()
        # df_faults_plot['date'] = df_faults_plot.index.date
        # df_faults_plot_reduced = df_faults_plot[df_faults_plot['date'] == df_faults_grouped['date'].iloc[0]]
        # # plot all variables in the same graph using index as x axis
        #
        # df_faults_plot_reduced.plot(
        #     subplots=True, figsize=(10, 10), grid=True, linestyle='-', linewidth=1,
        #     title=f"Rule {rule_name} - Date {str(df_faults_grouped['date'].iloc[0])}",
        #     drawstyle='steps-post',  # do not interpolate but scale
        # )
        #
        # # plot points red if faulty
        # plt.tight_layout()
        # # remove box from style
        # seaborn.despine(bottom=True)
        # # show gridline on all subplots
        # # plt.show()
    else:
        logger.info(f"No Faults found for {rule_name}")
        # # plot variables for a random day
        # df_plot = df.copy()
        # df_plot['date'] = df_plot.index.date
        # df_faults_grouped = df_plot.groupby('date')[rule_name].sum().reset_index()
        # # plot a random date iloc rand from 1 e length
        # date_random = randint(1, len(df_faults_grouped) - 3)
        # # plot 3 days
        # df_plot_reduced = df_plot[
        #     (
        #             (df_plot['date'] == df_faults_grouped['date'].iloc[date_random]) |
        #             (df_plot['date'] == df_faults_grouped['date'].iloc[date_random + 1]) |
        #             (df_plot['date'] == df_faults_grouped['date'].iloc[date_random + 2])
        #     )
        # ]
        # # plot all variables in the same graph using index as x axis
        #
        # df_plot_reduced.plot(
        #     subplots=True, figsize=(10, 10), grid=True, linestyle='-', linewidth=1,
        #     title=f"Rule {rule_name} - Date {str(df_faults_grouped['date'].iloc[date_random])}",
        #     drawstyle='steps-post',  # do not interpolate but scale
        #     legend='best'
        # )
        #
        # # plot points red if faulty
        # plt.tight_layout()
        # # remove box from style
        # seaborn.despine(bottom=True)
        # # show gridline on all subplots
        # plt.show()

    return df


def get_apar_params(si: bool = False, param_list: list = None) -> dict:
    """
    Get the predefined parameters for APAR rules.
    :param si: International system?
    :param param_list: List of parameters to return depending ont he applied rule
    :return: Dictionary of parameters
    """
    if si:
        # imperial units
        params_dict = {
            'e_t': 2,  # threshold for errors in temperature measurements
            'e_f': 0.3,  # threshold parameter accounting for errors related to airflows
            'e_hc': 0.1,  # threshold parameter for the heating coil valve control signal
            'e_cc': 0.1,  # threshold parameter for the cooling coil valve control signal
            'e_d': 0.02,  # threshold parameter for the mixing box damper control signal
            'dt_sf': 1.1,  # Supply Fan Temperature Rise
            'dt_rf': 1.1,  # Return Fan Temperature Rise
        }
    else:
        # °F error threshold parameters
        params_dict = {
            'e_t': 3.6,  # threshold for errors in temperature measurements
            'e_f': 0.3,  # threshold parameter accounting for errors related to airflows
            'e_hc': 0.02,  # threshold parameter for the heating coil valve control signal
            'e_cc': 0.02,  # threshold parameter for the cooling coil valve control signal
            'e_d': 0.02,  # threshold parameter for the mixing box damper control signal
            'dt_sf': 2,  # Supply Fan Temperature Rise
            'dt_rf': 2,  # Return Fan Temperature Rise
        }

    if param_list is not None:
        # find only the parameters that are needed
        return {key: params_dict[key] for key in param_list}
    else:
        raise ValueError("param_list must be a list of parameters to return")


def remove_cols(remove_flag: bool, df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """
    Remove a list of columns from a dataframe.

    :param remove_flag: Flag to enable/disable the removal of columns
    :param df: Dataframe to remove columns from
    :param cols: List of columns to remove
    :return: Dataframe with columns removed
    """

    if remove_flag:
        logger.info("Troubleshoot mode enabled - not removing helper columns")
        return df
    else:
        if cols is None:
            cols = ["lhs", "rhs"]
        for col in cols:
            del df[col]
        return df


class APAROperationalModes:
    """
    Define operational modes according to APAR definition.

    - 1	Heating	                                    MODE 1 (Heating)
    - 2	Cooling with outdoor air 	                MODE 2 (Cooling with outdoor air )
    - 3	Mechanical cooling with 100 % outdoor air 	MODE 3 (Mechanical cooling with 100 % outdoor air )
    - 4	Mechanical cooling with minimum outdoor air MODE 4 (Mechanical cooling with minimum outdoor air )
    - 5	Unknown 	                                MODE 5 (Unknown)
    - 0	All	                                        MODE 0 (All)

    """

    def __init__(
            self,
            oa_dmpr_sig_col: str,  # Outdoor air damper position sensor
            oat_col: str,  # Outdoor air temperature
            heating_sig_col: str,  # Heating coil position sensor
            cooling_sig_col: str,  # Cooling coil position sensor
            sys_ctl_col: str,  # System control status ON/OFF
            fan_vfd_speed_col: str,  # Supply fan speed
            troubleshoot=False,  # Troubleshoot mode
            fan_threshold: float = 0.01,  # Fan speed threshold
            valve_threshold: float = 0.05,  # Valve threshold
            damper_threshold: float = 0.05,  # Valve threshold
            eco_mode_temp_min: float = 33.8,  # Minimum temperature for eco mode
            eco_mode_temp_max: float = 60,  # Maximum temperature for eco mode
            si=True,  # SI units
    ):
        # assign variables to class
        self.oa_dmpr_sig_col = oa_dmpr_sig_col
        self.oat_col = oat_col
        self.heating_sig_col = heating_sig_col
        self.cooling_sig_col = cooling_sig_col
        self.sys_ctl_col = sys_ctl_col
        self.fan_vfd_speed_col = fan_vfd_speed_col
        # assign threshold to class
        self.valve_threshold = valve_threshold
        self.fan_threshold = fan_threshold
        self.damper_threshold = damper_threshold
        # convert units if needed
        if si:
            self.eco_mode_temp_min = fahrenheit_to_celsius(eco_mode_temp_min)
            self.eco_mode_temp_max = fahrenheit_to_celsius(eco_mode_temp_max)
        else:
            self.eco_mode_temp_min = eco_mode_temp_min
            self.eco_mode_temp_max = eco_mode_temp_max
        self.troubleshoot = troubleshoot

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """

        # copy to avoid warnings
        df1 = df.copy()

        # eventually normalize from 0-1 outdoor air damper position sensor
        df1 = normalize_01(df1, self.oa_dmpr_sig_col)
        df1 = normalize_01(df1, self.cooling_sig_col)
        df1 = normalize_01(df1, self.heating_sig_col)
        df1 = normalize_01(df1, self.fan_vfd_speed_col)
        df1 = normalize_01(df1, self.sys_ctl_col)

        # create a operating mode column by default unknown
        # MODE 5 (Unknown)
        df1['operating_mode'] = None

        '''
        Define Operational Mode (OM) ON/OFF in different ways
        1) Based on calendar schedule
        2) Based on system ON/OFF signal if available
        3) Based on fan speed (arbitrary threshold)
        4) Based on fan speed (data driven threshold)
        5) Based on cooling coil valve position and fan speed
        
        In this case we use system ON/OFF status
        '''

        df1['operating_mode'] = np.where(
            (df1[self.sys_ctl_col] != 0),  # this condition prevents aggregation values different from 1
            'OM_ON', 'OM_OFF')

        '''
        Define Operational Mode (OM) Economizer (OM_2_ECO) : 

        1) The AHU operates in economizer mode when outdoor air temperature is between 33.8°F and 60°F. 
        In this mode, the OA damper modulates in sequence with the RA damper to maintain a 55°F mixed air temperature 
        setpoint. Once the OA damper is greater than 100% open, the cooling coil valve shall be enabled to maintain 
        supply air temperature setpoint.
        2) Cooling valve closed and damper modulating

        '''

        # df1['operating_mode'] = np.where(
        #     (df1['operating_mode'] == 'OM_ON') &
        #     (df1[self.oat_col] >= 33.8) &
        #     (df1[self.oat_col] <= 60),
        #     'OM_ECO', df1['operating_mode'])

        df1['operating_mode'] = np.where(
            (df1['operating_mode'] == 'OM_ON') &
            (df1[self.cooling_sig_col] < self.valve_threshold) &  # valve closed
            (df1[self.oa_dmpr_sig_col] < 1 - self.damper_threshold) &  # max damper
            (df1[self.oa_dmpr_sig_col] > self.damper_threshold) &  # not closed
            # (df1[self.oa_dmpr_sig_col] > 0.1 + 0.05) # the minimum is not always kown
            (df1[self.oat_col] >= self.eco_mode_temp_min) &
            (df1[self.oat_col] <= self.eco_mode_temp_max),
            'OM_2_ECO', df1['operating_mode'])

        '''
        Define Operational Mode (OM) Cooling with outdoor air (OM_3_OUT) : 
        1) Cooling valve closed and damper open 100%
        '''

        df1['operating_mode'] = np.where(
            (df1['operating_mode'] == 'OM_ON') &
            (df1[self.cooling_sig_col] < self.valve_threshold) &  # valve closed
            (df1[self.oa_dmpr_sig_col] > 1 - self.damper_threshold),  # max damper
            'OM_3_OUT', df1['operating_mode'])

        '''
        Define Operational Mode (OM) Mechanical cooling with minimum outdoor air (OM_4_MIN) :
        '''

        df1['operating_mode'] = np.where(
            (df1['operating_mode'] == 'OM_ON') &
            (df1[self.cooling_sig_col] > self.valve_threshold) &  # valve modulating
            (df1[self.oa_dmpr_sig_col] < 0.1 + self.damper_threshold) &  # min damper + epsilon todo find minimum damper
            (df1[self.oa_dmpr_sig_col] > 0.1 - self.damper_threshold),  # min damper - epsilon
            'OM_4_MIN', df1['operating_mode'])

        '''
        Define Operational Mode (OM) 5 Unknown when is on and all the others do not apply
        '''
        df1['operating_mode'] = np.where(
            (df1['operating_mode'] == 'OM_ON'),
            'OM_5_UNKWN', df1['operating_mode'])

        return df1

    @staticmethod
    def print_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Print summary of the operational modes
        :param df: dataframe with the operational modes
        :return:
        """
        # summarize
        # create column with only 1
        df_modes_grouped = df.copy()
        df_modes_grouped['count'] = 1
        df_modes_grouped = df_modes_grouped.groupby('operating_mode')['count'].count().reset_index()
        # sort by fault descending
        df_modes_grouped = df_modes_grouped.sort_values(by='count', ascending=False)
        # transform to percentage
        df_modes_grouped['percentage'] = round(df_modes_grouped['count'] / df_modes_grouped['count'].sum() * 100, 2)
        # drop count
        df_modes_grouped = df_modes_grouped.drop(columns=['count'])
        # print formatted dataframe
        df_modes_grouped = df_modes_grouped.rename(
            columns={'operating_mode': 'Operating Mode', 'percentage': 'Time [%]'}
        )
        return df_modes_grouped

    def plot(self, df: pd.DataFrame) -> None:
        """
        Plots histograms for each variable used for the determination of the operating mode
        :param df: Original dataframe
        :return plt: Plot
        """
        # create a figure with subplots

        df_long = df.melt(
            id_vars=['operating_mode'],
            value_vars=[self.cooling_sig_col, self.fan_vfd_speed_col, self.oa_dmpr_sig_col],
            var_name='variable', value_name='values'
        )

        g = seaborn.FacetGrid(df_long, row="variable", col="operating_mode", hue="variable", aspect=2)
        g.map_dataframe(seaborn.histplot, x="values", binwidth=0.05, alpha=0.5)
        # add x ticks every 10
        for ax in g.axes.flat:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))

        g.add_legend()
        plt.show()


class APAR01:
    """
    In heating mode, supply air temp should be greater than mixed air temp. Tsa<Tma+∆Tsf-εt
    """

    def __init__(
            self,
            mat_col: str,  # Tma (mixed air temperature)
            sat_col: str,  # Tsa (supply air temperature)
            mode: list,  # Operational mode that apply
            troubleshoot=False,  # Troubleshoot mode
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_sf'])
        self.e_t = param_list['e_t']
        self.dt_sf = param_list['dt_sf']  # usually not present in datasets
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.mat_col = mat_col
        self.troubleshoot = troubleshoot

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()
        # calculate right hand side and left hand side of the rule and apply condition
        lhs = df[self.sat_col]
        rhs = df[self.mat_col] + self.dt_sf - self.e_t
        df1[self.rule_name] = (lhs < rhs).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1

    def plot(self, df: pd.DataFrame) -> Figure:
        """
        Plot the fault
        :param df: Original dataframe
        :return: None
        """
        fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 6))
        plt.title(self.rule_name)

        ax1.plot(df.index, df[self.mat_col], color='g', label="Mix Temp")
        ax1.plot(df.index, df[self.sat_col], color='b', label="Supply Temp")

        ax1.legend(loc='best')
        ax1.set_ylabel("°F")

        ax2.plot(df.index, df[self.rule_name], label="Fault", color="k")
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Fault Flags')
        ax2.legend(loc='best')

        plt.legend()
        plt.tight_layout()

        return fig


class APAR05:
    """
    Outdoor air temp is too warm for cooling with outdoor air. Toa>Tsa,s-∆Tsf+εt
    """

    def __init__(
            self,
            oat_col: str,  # T_oa (outside air temperature)
            satsp_col: str,  # T_sa,s (supply air temperature setpoint)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_sf'])
        self.e_t = param_list['e_t']
        self.dt_sf = param_list['dt_sf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.satsp_col = satsp_col
        self.oat_col = oat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Toa>Tsa,s-∆Tsf+εt
        df1[self.rule_name] = (
                df[self.oat_col] > df[self.satsp_col] - self.dt_sf + self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR06:
    """
    Supply air temp should be less than return air temp.Tsa>Tra-∆Trf+εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            rat_col: str,  # T_ra (return air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_rf'])
        self.e_t = param_list['e_t']
        self.dt_rf = param_list['dt_rf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.rat_col = rat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa>Tra-∆Trf+εt
        df1[self.rule_name] = (
                df[self.sat_col] > df[self.rat_col] - self.dt_rf + self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR07:
    """
    Supply and mixed air temp should be nearly the same.|Tsa-∆Tsf-Tma|>εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            mat_col: str,  # T_ma (mixed air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_sf'])
        self.e_t = param_list['e_t']
        self.dt_sf = param_list['dt_sf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.mat_col = mat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa>Tra-∆Trf+εt
        df1[self.rule_name] = (
                np.abs(df[self.sat_col] - df[self.mat_col] - self.dt_sf) > self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR08:
    """
    Outdoor air temperature is too cool for mechanical cooling with 100% outdoor air. Toa < Tsa,s - ∆Tsf - εt
    """

    def __init__(
            self,
            oat_col: str,  # T_oa (outside air temperature)
            satsp_col: str,  # T_sa,s (supply air temperature setpoint)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_sf'])
        self.e_t = param_list['e_t']
        self.dt_sf = param_list['dt_sf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.oat_col = oat_col
        self.satsp_col = satsp_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa>Tra-∆Trf+εt
        df1[self.rule_name] = (
                df[self.oat_col] < df[self.satsp_col] - self.dt_sf - self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR10:
    """
    Outdoor and mixed air temp should be nearly the same. |Toa-Tma|>εt
    """

    def __init__(
            self,
            oat_col: str,  # T_oa (outside air temperature)
            mat_col: str,  # T_ma (mixed air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t'])
        self.e_t = param_list['e_t']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.oat_col = oat_col
        self.mat_col = mat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa>Tra-∆Trf+εt
        df1[self.rule_name] = (
                np.abs(df[self.oat_col] - df[self.mat_col]) > self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR11:
    """
    Supply air temp should be less than mixed air temp. Tsa> Tma+∆Tsf+εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            mat_col: str,  # T_ma (mixed air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_sf'])
        self.e_t = param_list['e_t']
        self.dt_sf = param_list['dt_sf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.mat_col = mat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa>Tra-∆Trf+εt
        df1[self.rule_name] = (
                df[self.sat_col] > df[self.mat_col] + self.dt_sf + self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR12:
    """
    Supply air temp should be less than return air temp.Tsa>Tra-∆Trf+εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            rat_col: str,  # T_ra (return air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_rf'])
        self.e_t = param_list['e_t']
        self.dt_rf = param_list['dt_rf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.rat_col = rat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa>Tra-∆Trf+εt
        df1[self.rule_name] = (
                df[self.sat_col] > df[self.rat_col] - self.dt_rf + self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR13:
    """
     Cooling coil valve command is fully open and supply air temp error exists. |ucc – 1| ≤ εcc and Tsa – Tsa,s ≥ εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            satsp_col: str,  # T_sa,s (supply air temperature setpoint)
            mode: list,  # Operational mode that apply
            cooling_sig_col: str,  # u_cc (normalized heating coil valve control signal [0,1])
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_cc', 'e_t'])
        self.e_cc = param_list['e_cc']
        self.e_t = param_list['e_t']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.cooling_sig_col = cooling_sig_col
        self.sat_col = sat_col
        self.satsp_col = satsp_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()
        # calculate right hand side and left hand side of the rule and apply condition

        df1[self.rule_name] = (
                (np.abs(df[self.cooling_sig_col] - 1) <= self.e_cc) &
                (df[self.sat_col] - df[self.satsp_col] >= self.e_t)
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR14:
    """
    Cooling coil valve command is fully open. If cooling load increases, supply air temp will drift from setpoint.
    |ucc – 1| ≤ εcc
    """

    def __init__(
            self,
            cooling_sig_col: str,  # u_cc (normalized heating coil valve control signal [0,1])
            mode: list,  # Operational mode that apply
            troubleshoot=False,  # Troubleshoot mode
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_cc'])
        self.e_cc = param_list['e_cc']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.cooling_sig_col = cooling_sig_col
        self.troubleshoot = troubleshoot

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()
        df1[self.rule_name] = (
                np.abs(df[self.cooling_sig_col] - 1) <= self.e_cc
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR16:
    """
    Supply air temp should be less than return air temp.Tsa>Tra-∆Trf+εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            mat_col: str,  # T_ma (mixed air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_sf'])
        self.e_t = param_list['e_t']
        self.dt_sf = param_list['dt_sf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.mat_col = mat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa > Tma +∆Tsf +εt
        df1[self.rule_name] = (
                df[self.sat_col] > df[self.mat_col] + self.dt_sf + self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR17:
    """
    Supply air temp should be less than return air temp.Tsa>Tra-∆Trf+εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            rat_col: str,  # T_ra (return air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t', 'dt_rf'])
        self.e_t = param_list['e_t']
        self.dt_rf = param_list['dt_rf']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.rat_col = rat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tsa>Tra-∆Trf+εt
        df1[self.rule_name] = (
                df[self.sat_col] > df[self.rat_col] - self.dt_rf + self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR19:
    """
     Cooling coil valve command is fully open and supply air temp error exists. |ucc – 1| ≤ εcc and Tsa – Tsa,s ≥ εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            satsp_col: str,  # T_sa,s (supply air temperature setpoint)
            mode: list,  # Operational mode that apply
            cooling_sig_col: str,  # u_cc (normalized heating coil valve control signal [0,1])
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_cc', 'e_t'])
        self.e_cc = param_list['e_cc']
        self.e_t = param_list['e_t']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.cooling_sig_col = cooling_sig_col
        self.sat_col = sat_col
        self.satsp_col = satsp_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()
        # calculate right hand side and left hand side of the rule and apply condition

        df1[self.rule_name] = (
                (np.abs(df[self.cooling_sig_col] - 1) <= self.e_cc) &
                (df[self.sat_col] - df[self.satsp_col] >= self.e_t)
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR20:
    """
    Cooling coil valve command is fully open. If cooling load increases, supply air temp will drift from setpoint. |ucc – 1| ≤ εcc
    """

    def __init__(
            self,
            cooling_sig_col: str,  # u_cc (normalized heating coil valve control signal [0,1])
            mode: list,  # Operational mode that apply
            troubleshoot=False,  # Troubleshoot mode
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_cc'])
        self.e_cc = param_list['e_cc']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.cooling_sig_col = cooling_sig_col
        self.troubleshoot = troubleshoot

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        df1[self.rule_name] = (
                np.abs(df[self.cooling_sig_col] - 1) <= self.e_cc
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR24:
    """
    Cooling coil valve and mixing box dampers are both modulating simultaneously. εd < ud<1-εd and ucc>εcc
    """

    def __init__(
            self,
            mix_damper_sig_col: str,  # u_d (normalized mixing box damper control signal [0,1] )
            cooling_sig_col: str,  # u_cc (normalized heating coil valve control signal [0,1])
            mode: list,  # Operational mode that apply
            troubleshoot=False,  # Troubleshoot mode
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_d', 'e_cc'])
        self.e_d = param_list['e_d']
        self.e_cc = param_list['e_cc']
        self.mode = mode

        self.rule_name = type(self).__name__  # get class name
        self.mix_damper_sig_col = mix_damper_sig_col
        self.cooling_sig_col = cooling_sig_col
        self.troubleshoot = troubleshoot

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        df1[self.rule_name] = (
                (self.e_d < df1[self.mix_damper_sig_col]) &
                (df1[self.mix_damper_sig_col] < 1 - self.e_d) &
                (df1[self.cooling_sig_col] > self.e_cc)
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR25:
    """
    Persistent supply air temp error exists. | Tsa – Tsa,s | > εt
    """

    def __init__(
            self,
            sat_col: str,  # T_sa (supply air temperature)
            satsp_col: str,  # T_sa,s (supply air temperature setpoint)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t'])
        self.e_t = param_list['e_t']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.sat_col = sat_col
        self.satsp_col = satsp_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """

        # copy to avoid warnings
        df1 = df.copy()

        if check_low_variance(df, self.sat_col):
            # if stuck sensor all faluty independent to OM
            df1[self.rule_name] = 1
        else:
            # check rule and operational mode
            df1[self.rule_name] = (
                    np.abs(df[self.sat_col] - df[self.satsp_col]) > self.e_t
            ).astype(int).values

            df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR26:
    """
    Mixed air temp should be between return and outdoor air temp (mixed air temp too great). Tma < min(Tra , Toa) - εt
    """

    def __init__(
            self,
            mat_col: str,  # T_ma (mixed air temperature)
            rat_col: str,  # T_ra (return air temperature)
            mode: list,  # Operational mode that apply
            oat_col: str,  # T_oa (outside air temperature)
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t'])
        self.e_t = param_list['e_t']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.mat_col = mat_col
        self.rat_col = rat_col
        self.oat_col = oat_col

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()
        df1[self.rule_name] = (
                df[self.mat_col] < np.minimum(df[self.rat_col], df[self.oat_col]) - self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1


class APAR27:
    """
    Mixed air temp should be between return and outdoor air temp (mixed air temp too low). Tma > max(Tra , Toa) + εt
    """

    def __init__(
            self,
            mat_col: str,  # T_ma (mixed air temperature)
            rat_col: str,  # T_ra (return air temperature)
            oat_col: str,  # T_oa (outside air temperature)
            mode: list,  # Operational mode that apply
            si=True,  # International system?
    ):
        param_list = get_apar_params(si=si, param_list=['e_t'])
        self.e_t = param_list['e_t']
        self.mode = mode
        self.rule_name = type(self).__name__  # get class name
        self.mat_col = mat_col
        self.rat_col = rat_col
        self.oat_col = oat_col

    def plot(self, df: pd.DataFrame):
        """
        Plots the rule
        :return: None
        """
        # copy to avoid warnings
        df1 = df.copy()
        df1['Date'] = df1.index.date
        df1 = df1.groupby(['Date']).agg(
            {
                self.oat_col: 'mean',
                self.mat_col: 'mean',
                self.rat_col: 'mean',
            }
        ).reset_index()

        # create scatter plot of mixed air temperature vs return air temperature
        # using matplotlib
        fig, ax = plt.subplots()
        ax.scatter(
            df1[self.oat_col],
            df1[self.rat_col],
            c="blue",
        )
        ax.scatter(
            df1[self.oat_col],
            df1[self.mat_col],
            c="red",
        )
        ax.legend(["Return Air Temperature", "Mixed Air Temperature"])
        ax.set_xlabel("Mean daily outdoor air temperature [C]")
        ax.set_ylabel("Air Temperature")
        ax.set_title(f"{self.rule_name} scatter plot")
        plt.show()

        return plt

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs analytics logic
        :param df: Original dataframe
        :return: Dataframe with fault tag
        """
        # copy to avoid warnings
        df1 = df.copy()

        # Tma > max(Tra , Toa) + εt
        df1[self.rule_name] = (
                df[self.mat_col] > np.maximum(df[self.rat_col], df[self.oat_col]) + self.e_t
        ).astype(int).values

        df1 = exclude_operating_modes(df=df1, operating_modes=self.mode, rule_name=self.rule_name)

        return df1
