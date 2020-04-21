#!/usr/bin/python
'''
    This is a python script which will create
    any figures of our processed dataset
'''
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sys.path.append('../')
from utils.file_util import load_yaml

#Global
CONFIG_PATH = './visualize_config.yml'

def main():
    '''main'''
    config = load_yaml(CONFIG_PATH)
    processed_csv_path = config['processed_path']
    figure_output_path = config['figure_output_path']

    sns.set(style='ticks', color_codes=True)
    print('Creating Figures....')
    processed_df = pd.read_csv(processed_csv_path)
    plot_base_frequencies(processed_df, figure_output_path)
    plot_base_features(processed_df, figure_output_path)
    plot_engineered_features(processed_df, figure_output_path)
    print(f'Creation Completed. Find output at: {figure_output_path}')

def plot_base_frequencies(processed_df, output_base_path):
    '''
        Plots frequency count for Dir, Proto, State, sTos, and dTos
    '''
    #Dir Count
    axes = plt.subplots(figsize=(10, 5))
    axes = sns.barplot()
    axes = sns.countplot(x='Dir', hue='Label', palette='husl', data=processed_df)
    save_png(axes.get_figure(), output_base_path, 'dir_count')
    plt.clf()

    #Proto Count
    axes = plt.subplots(figsize=(10, 5))
    axes = sns.barplot()
    axes = sns.countplot(x='Proto', hue='Label', palette='husl', data=processed_df)
    save_png(axes.get_figure(), output_base_path, 'proto_count')
    plt.clf()

    #Dur VS Label
    axes = sns.scatterplot(x='Dur', y='Label', palette='husl', data=processed_df)
    save_png(axes.get_figure(), output_base_path, 'dur_vs_label')
    plt.clf()

    #State Count
    axes = plt.subplots(figsize=(16, 8))
    axes = sns.barplot()
    axes = sns.countplot(x='State', hue='Label', palette='husl', ax=axes, data=processed_df)
    axes.set_xticklabels(axes.get_xticklabels(), rotation=45)
    save_png(axes.get_figure(), output_base_path, 'state_count')
    plt.clf()

    #Sport Count
    axes = plt.subplots(figsize=(10, 5))
    axes = sns.barplot()
    axes = sns.countplot(x='Sport_Int', hue='Label', palette='husl', data=processed_df)
    save_png(axes.get_figure(), output_base_path, 'sport_count')
    plt.clf()

    #Dport Count
    axes = plt.subplots(figsize=(10, 5))
    axes = sns.barplot()
    axes = sns.countplot(x='Dport_Int', hue='Label', palette='husl', data=processed_df)
    save_png(axes.get_figure(), output_base_path, 'dport_count')
    plt.clf()

def save_png(fig, output_base_path, file_name):
    '''Saves the given figure to a png file'''
    file_format = '.png'
    fig.savefig(output_base_path + file_name + file_format)

def plot_and_save_pairplot(dataframe, x_vars, y_vars, output_base_path, file_name):
    '''
        Will create a seaborn pairplot with a given dataframe, x and y variables
        on hue Label (Malicious 1, Benign 0)
        Saves to output path with provided file name.
    '''
    plt.clf()
    sns_plot = sns.pairplot(dataframe,
                            hue='Label',
                            kind='scatter',
                            palette='husl',
                            x_vars=x_vars,
                            y_vars=y_vars)
    sns_plot.savefig(f'{output_base_path}{file_name}.png')

def plot_base_features(processed_df, output_base_path):
    '''
        Plots PairWise Dur, TotPkts, TotBytes, SrcBytes.
        Compares between Malicious and Benign
    '''
    vars_l = ['Dur', 'TotPkts', 'TotBytes', 'SrcBytes']
    sns_plot = sns.pairplot(processed_df, hue='Label', kind='scatter', palette='husl', vars=vars_l)
    sns_plot.savefig(output_base_path + 'base_features.png')

def plot_engineered_features(processed_df, output_base_path):
    '''
        Plotting various engineered features to determine any relations
    '''
    #TotBytesVsTotPkt_10T
    x_vars = [
        'TotBSumFwd_10T',
        'TotBMinFwd_10T',
        'TotBMaxFwd_10T',
        'TotBMeanFwd_10T',
        'TotBStdFwd_10T',
        'TotBSumBwd_10T',
        'TotBMinBwd_10T',
        'TotBMaxBwd_10T',
        'TotBMeanBwd_10T',
        'TotBStdBwd_10T'
    ]

    y_vars = [
        'TotPktSumFwd_10T',
        'TotPktMinFwd_10T',
        'TotPktMaxFwd_10T',
        'TotPktMeanFwd_10T',
        'TotPktStdFwd_10T',
        'TotPktSumBwd_10T',
        'TotPktMinBwd_10T',
        'TotPktMaxBwd_10T',
        'TotPktMeanBwd_10T',
        'TotPktStdBwd_10T',
    ]
    plot_and_save_pairplot(processed_df, x_vars, y_vars, output_base_path, 'TotBytesVsTotPkt_10T')

    # TotBytesFwdVsSrcBytes_10T
    x_vars = [
        'TotBSumFwd_10T',
        'TotBMinFwd_10T',
        'TotBMaxFwd_10T',
        'TotBMeanFwd_10T',
        'TotBStdFwd_10T',
        'TotBSumBwd_10T',
        'TotBMinBwd_10T',
        'TotBMaxBwd_10T',
        'TotBMeanBwd_10T',
        'TotBStdBwd_10T',
    ]

    y_vars = [
        'SrcBSumFwd_10T',
        'SrcBSumBwd_10T',
        'SrcBMinFwd_10T',
        'SrcBMinBwd_10T',
        'SrcBMaxFwd_10T',
        'SrcBMaxBwd_10T',
        'SrcBMeanFwd_10T',
        'SrcBMeanBwd_10T',
        'SrcBStdFwd_10T',
        'SrcBStdBwd_10T'
    ]
    plot_and_save_pairplot(processed_df, x_vars, y_vars, output_base_path, 'TotBFwdVsSrcB_10T')

    # TotPktVsSrcB_10T
    x_vars = [
        'TotPktSumFwd_10T',
        'TotPktMinFwd_10T',
        'TotPktMaxFwd_10T',
        'TotPktMeanFwd_10T',
        'TotPktStdFwd_10T',
        'TotPktSumBwd_10T',
        'TotPktMinBwd_10T',
        'TotPktMaxBwd_10T',
        'TotPktMeanBwd_10T',
        'TotPktStdBwd_10T'
    ]

    y_vars = [
        'SrcBSumFwd_10T',
        'SrcBSumBwd_10T',
        'SrcBMinFwd_10T',
        'SrcBMinBwd_10T',
        'SrcBMaxFwd_10T',
        'SrcBMaxBwd_10T',
        'SrcBMeanFwd_10T',
        'SrcBMeanBwd_10T',
        'SrcBStdFwd_10T',
        'SrcBStdBwd_10T'
    ]
    plot_and_save_pairplot(processed_df, x_vars, y_vars, output_base_path, 'TotPktVsSrcB_10T')
    #TimeBetween2Flows
    x_vars = [
        'STime2FlowFwdN_5',
        'STime2FlowBwdN_5',
        'DSrcBStdBwdN_5',
        'DTime2FlowFwdN_5',
        'DTime2FlowBwdN_5',
        'STime2FlowFwd_10T',
        'STime2FlowBwd_10T',
        'DTime2FlowFwd_10T',
        'DTime2FlowBwd_10T'
    ]
    plot_and_save_pairplot(processed_df, x_vars, x_vars, output_base_path, 'TimeBetween2Flows')

    #Time2FlowVsStdN_5
    x_vars = [
        'STime2FlowFwdN_5',
        'DTime2FlowFwdN_5',
        'STotBStdFwdN_5',
        'DTotBStdFwdN_5',
        'STotPktStdFwdN_5',
        'SSrcBStdFwdN_5'
    ]
    plot_and_save_pairplot(processed_df, x_vars, x_vars, output_base_path, 'Time2FlowVsStdN_5')

if __name__ == '__main__':
    main()
