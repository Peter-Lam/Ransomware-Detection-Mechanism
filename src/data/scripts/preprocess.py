#!/usr/bin/python
'''
    This is a python program will create preproccesed.csv
    To be called in src/data/make_dataset.py
'''
from os import makedirs
from os.path import dirname

import pandas as pd

from utils.file_util import load_yaml

def main():
    '''main'''
    make_preprocess()

def make_preprocess():
    '''
        Read interim.csv and clean more data.
        1. Read StartTime as DateTime
        2. Perform binning on source and destination ports
        3. Add attribute indicating direction of flow
        4. Write to preproccessed.csv
    '''
    config = load_yaml('./config.yml')
    interim_output_path = config['interim_output_path']
    preprocessed_output_path = config['preprocessed_output_path']

    # Well-known ports range from 0 through 1023
    # Registered ports are 1024 to 49151
    # Dynamic ports (also called private ports) are 49152 to 65535
    port_bins = [0, 1023, 49151, 65535]
    labels = [1, 2, 3]

    interim_df = pd.read_csv(interim_output_path,
                             sep=',',
                             escapechar='\\')
    interim_df['StartTime'] = pd.to_datetime(interim_df['StartTime'])

    interim_df['Sport_bin'] = pd.cut(interim_df['Sport'], bins=port_bins,
                                     labels=labels, include_lowest=True)

    interim_df['Dport_bin'] = pd.cut(interim_df['Dport'], bins=port_bins,
                                     labels=labels, include_lowest=True)

    interim_df['is_fwd'] = interim_df['Sport']
    interim_df.loc[interim_df['Sport'] >= 1024, 'is_fwd'] = 1
    interim_df.loc[interim_df['Sport'] < 1024, 'is_fwd'] = 0

    preprocessed_df = interim_df.copy()
    makedirs(dirname(preprocessed_output_path), exist_ok=True)
    preprocessed_df.to_csv(preprocessed_output_path, index=False)
