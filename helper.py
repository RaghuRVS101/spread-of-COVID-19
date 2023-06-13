import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as md

from pathlib import Path
import os


OUTPUT_NAME = 'a3-covid-simulation.png'
def get_filepath(filename):
    '''
    Returns full file path 
    '''
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    filepath = os.path.join(source_dir,filename)
    return filepath

def save_plot(fig, filename):
    filepath = get_filepath(filename)    
    fig.savefig(filepath,dpi=300)

def read_dataset(filename):

    filepath = get_filepath(filename)

    df = pd.read_csv(filepath, sep=',', header= 0)

    return df

def create_plot(summary_df, countries):
    '''
    Creates a plot from the time series of the infection states

    input:
    summary_df: DataFrame containing the infection states
    countries: list of countries to include in the plot
    '''
    print(f'Plotting is being prepared for the following dataset ...')
    print(summary_df)

    # filter the data by selected countries
    states_timeseries_df = summary_df[summary_df['country'].isin(countries)]
    states_timeseries_df = states_timeseries_df[['country','date', 'H', 'I', 'S', 'M', 'D']]
    states_timeseries_df['date'] = pd.to_datetime(states_timeseries_df['date'])
    states_timeseries_df.set_index('date')

    # Multiple countries in subfigures
    countries_num = len(countries)
    fig, ax = plt.subplots(countries_num, figsize =(16,9*countries_num))
    for i in range(countries_num):
 
        states_timeseries_df[states_timeseries_df['country']==countries[i]].plot(
            kind= 'bar', 
            x= 'date', 
            stacked=True, 
            width = 1, 
            color=['green', 'darkorange', 'indianred', 'lightseagreen', 'slategray'],
            ax = ax[i])

        ax[i].legend(['Healthy', 'Infected (without symptoms)', 'Infected (with symptoms)', 'Immune', 'Deceased'])
        ax[i].set_xticklabels(ax[i].get_xticks(), rotation = 30)
        plot_name = countries[i]
        ax[i].set_title(f"Covid Infection Status in {plot_name}")
        ax[i].set_xlabel("Date")
        ax[i].set_ylabel("Population in Millions")

        ax[i].xaxis.set_major_locator(md.MonthLocator())
        selected_dates = states_timeseries_df['date'].dt.to_period('M').unique()
        ax[i].set_xticklabels(selected_dates.strftime('%b %Y'), rotation=30, horizontalalignment= "center")

    save_plot(fig, f'{OUTPUT_NAME}')
    print(f'Plotting Done!')

