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
    s_labels = ['sis_known_port', 'sis_reg_port', 'sis_dyn_port']
    d_labels = ['dis_known_port', 'dis_reg_port', 'dis_dyn_port']

    interim_df = pd.read_csv(interim_output_path,
                             sep=',',
                             escapechar='\\')
    preprocessed_df = interim_df
    preprocessed_df['StartTime'] = pd.to_datetime(preprocessed_df['StartTime'])

    s_port_series = pd.cut(preprocessed_df['Sport'], bins=port_bins,
                           labels=s_labels, include_lowest=True)

    d_port_series = pd.cut(preprocessed_df['Dport'], bins=port_bins,
                           labels=d_labels, include_lowest=True)

    preprocessed_df['is_fwd'] = preprocessed_df['Sport']
    preprocessed_df.loc[preprocessed_df['Sport'] >= 1024, 'is_fwd'] = 1
    preprocessed_df.loc[preprocessed_df['Sport'] < 1024, 'is_fwd'] = 0

    preprocessed_df = preprocessed_df.join(pd.get_dummies(preprocessed_df['Proto']))
    preprocessed_df = preprocessed_df.join(pd.get_dummies(s_port_series))
    preprocessed_df = preprocessed_df.join(pd.get_dummies(preprocessed_df['Dir']))
    preprocessed_df = preprocessed_df.join(pd.get_dummies(d_port_series))
    preprocessed_df = preprocessed_df.join(pd.get_dummies(preprocessed_df['State']))

    makedirs(dirname(preprocessed_output_path), exist_ok=True)
    preprocessed_df.to_csv(preprocessed_output_path, index=False)
