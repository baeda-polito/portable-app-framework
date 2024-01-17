"""
Author:       Roberto Chiosa
Copyright:    Roberto Chiosa, © 2023
Email:        roberto.chiosa@polito.it

Created:      15/09/23
Script Name:  util_plot.py
Path:         utils

Script Description:


Notes:
"""

import os

import plotly.express as px


def plot_histogram(df, filename=None):
    """
    Plot the histogram of the variables
    :param filename: name of the dataset
    :param df: the dataframe containing the variables
    :return: 
    """
    p = px.histogram(df, x='value', y='value',
                     color='variable',
                     facet_col='variable',
                     histnorm='probability density',
                     marginal='box',
                     facet_col_wrap=3,
                     )
    p.update_yaxes(matches=None, showticklabels=True)
    # wandb.log({'VARIABLES DISTRIBUTIONS': p})
    p.update_layout(xaxis_title='', yaxis_title='')

    p.write_html(os.path.join('results', f'{filename}_HISTOGRAM.html'))


def plot_timeseries_transient(df, configuration: dict, filename=None):
    """
    Plot the timeseries of the variables with relative transient score and threshold
    :param filename: name of the dataset
    :param df: the dataframe containing the variables
    :param configuration: a dictionary of thresholds
    """

    p = px.bar(df, x='time', y='slope', title='Slope of cooling signal')
    # add cooling signal
    p.add_scatter(x=df['time'], y=df['cooling_sig_col'], name='cooling signal',
                  mode='lines')
    # p.add_scatter(x=df['time'], y=df['heating_sig_col'], name='heating signal',
    #               mode='lines')
    p.add_scatter(x=df['time'], y=df['oa_dmpr_sig_col'], name='damper signal',
                  mode='lines')
    p.update_layout(xaxis_title='Time',
                    yaxis_title='Value',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
    p.add_hrect(y0=0, y1=configuration["transient_cutoff"], col=1,
                annotation_text="transient_cutoff", annotation_position="left",
                fillcolor="grey", opacity=0.5, line_width=0)
    # p.show()
    p.write_html(os.path.join('results', f'{filename}_TRANSIENT.html'))


def plot_damper(df, configuration: dict, filename=None):
    """
    Plot the outdoor air damper control signal vs outdoor air fraction
    :param filename: the name of the file
    :param configuration:  a dictionary of thresholds
    :param df:  the dataframe containing the variables
    """
    # trim the distribution below 50%

    p = px.scatter(df,
                   x='oa_dmpr_sig_col',
                   y='oaf',
                   color='slope',
                   symbol='slope',
                   hover_data=['time', 'oat_col', 'slope'],
                   # marginal_x="histogram", marginal_y="histogram"
                   )
    p.update_layout(xaxis_title='Outdoor air damper control signal',
                    yaxis_title='Outdoor air fraction',
                    xaxis_range=[0, 1],
                    yaxis_range=[0, 1],
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
    p.add_vrect(x0=0, x1=configuration["damper_cutoff"], col=1,
                annotation_text="damper_cutoff", annotation_position="top left",
                fillcolor="grey", opacity=0.5, line_width=0)

    # Add '°C' to x-axis tick labels
    p.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1,
                   spikecolor="black",
                   tickformat='.0%', title_font=dict(size=14),
                   tickfont=dict(size=12, color='black'))
    p.update_yaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1,
                   spikecolor="black",
                   tickformat='.0%', title_font=dict(size=14),
                   tickfont=dict(size=12, color='black'))
    p.update_traces(
        hovertemplate='%{customdata[0]|%Y %B %d}<br>%{customdata[0]|%A, %H:%M}'
                      '<br><br>y = %{y:.2f}%<br>x = %{x:.2f}%<br>%{customdata[2]}<br>'
                      'Outdoor air temperature: %{customdata[1]:.2f}°C')

    p.write_html(os.path.join('results', f'{filename}_DAMPER.html'))


def plot_valves(df, configuration: dict, filename=None):
    """
    Plot the valve control signal vs DT across coil
    :param filename: the name of the file
    :param df: the dataframe containing the variables
    :param configuration: a dictionary of thresholds
    :return:
    """
    df.dropna(inplace=True)
    p = px.scatter(df,
                   x='value',
                   y='dt',
                   opacity=0.6,
                   color='variable',
                   color_discrete_map={'cooling_sig_col': "#01c5f4",
                                       'heating_sig_col': "#fe7201"},
                   symbol='slope',
                   # facet_col='variable',
                   hover_data=['time', 'oat_col', 'slope'],
                   # marginal_x="histogram", marginal_y="histogram"
                   )
    p.add_vrect(x0=0, x1=configuration["valves_cutoff"], col=1,
                annotation_text="valves_cutoff", annotation_position="bottom left",
                fillcolor="grey", opacity=0.5, line_width=0)
    p.add_hline(y=0, line_width=2, line_dash="dot", line_color="black", opacity=0.5)

    p.update_layout(xaxis_title='Valve control signal', yaxis_title='DT across coil',
                    xaxis_range=[0, 1], yaxis_range=[-20, 20],
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                    )
    p.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across",
                   spikethickness=1,
                   spikecolor="black", tickformat='.0%', title_font=dict(size=14),
                   tickfont=dict(size=12, color='black'))
    p.update_yaxes(showspikes=True, spikesnap="cursor", spikemode="across",
                   spikethickness=1,
                   spikecolor="black", tickformat='°C', title_font=dict(size=14),
                   tickfont=dict(size=12, color='black'))
    p.update_traces(
        hovertemplate='%{customdata[0]|%Y %B %d}<br>%{customdata[0]|%A, %H:%M}'
                      '<br><br>y = %{y:.2f}<br>x = %{x:.2f}%<br>%{customdata[2]}'
                      '<br>Outdoor air temperature: %{customdata[1]:.2f}°C')

    p.write_html(os.path.join('results', f'{filename}_VALVES.html'))
