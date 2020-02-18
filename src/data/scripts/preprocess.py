#!/usr/bin/python
'''
    This is a python program will create preproccesed.csv
    To be called in src/data/make_dataset.py
'''
from os import makedirs
from os.path import dirname

import numpy as np
import pandas as pd

from utils.file_util import load_yaml

def main():
    '''main'''
    make_preprocess()

def make_preprocess():
    '''
        Read interim.csv and clean more data.
        1. Read StartTime as DateTime
        2. Replace null values for sTos and dTos with -1
        3. Perform adaptive binning on sTos and use same
            bin for dTos (8-Quartile)
        4. Apply natural log on TotPkts, TotBytes, SrcBytes columns
            to remove skewing
        5. Write to preproccessed.csv
    '''
    config = load_yaml('./config.yml')
    interim_output_path = config['interim_output_path']
    preprocessed_output_path = config['preprocessed_output_path']
    quantile_list = [0, .125, .25, .375, .5, .625, .75, .875, 1.]
    labels = [1, 2, 3, 4, 5, 6, 7, 8]
    interim_df = pd.read_csv(interim_output_path,
                             sep=',', engine='python', escapechar='\\')
    interim_df['StartTime'] = pd.to_datetime(interim_df['StartTime'])
    interim_df.loc[interim_df['sTos'].replace('', np.nan).isnull(), 'sTos'] = -1
    interim_df.loc[interim_df['dTos'].replace('', np.nan).isnull(), 'dTos'] = -1
    bins_src_port = interim_df['Sport'].quantile(quantile_list)

    interim_df['Sport'] = pd.cut(interim_df['Sport'], bins=bins_src_port,
                                 labels=labels, include_lowest=True)

    interim_df['Dport'] = pd.cut(interim_df['Dport'], bins=bins_src_port,
                                 labels=labels, include_lowest=True)

    for col in ['Sport', 'Dport']:
        interim_df[col] = interim_df[col].astype('int64')
    for col in ['TotPkts', 'TotBytes', 'SrcBytes']:
        interim_df[col] = np.log((1 + interim_df[col]))

    preprocessed_df = interim_df.copy()
    makedirs(dirname(preprocessed_output_path), exist_ok=True)
    preprocessed_df.to_csv(preprocessed_output_path, index=False)
