#!/usr/bin/python
'''
    This is a python program will create preproccesed.csv
    To be called in src/data/make_dataset.py
'''
from os import makedirs
from os.path import dirname

import sys
import pandas as pd

sys.path.append('../')
from utils.file_util import load_yaml, load_json

#Global
CONFIG_PATH = './config.yml'

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
    config = load_yaml(CONFIG_PATH)
    interim_output_path = config['interim_output_path']
    preprocessed_output_path = config['preprocessed_output_path']
    proto_dict = load_json(config['proto_dict_path'])
    dir_dict = load_json(config['dir_dict_path'])
    state_dict = load_json(config['state_dict_path'])
    # Well-known ports range from 0 through 1023
    # Registered ports are 1024 to 49151
    # Dynamic ports (also called private ports) are 49152 to 65535
    port_bins = [0, 1023, 49151, 65535]
    port_labels = [0, 1, 2]

    interim_df = pd.read_csv(interim_output_path,
                             sep=',',
                             escapechar='\\')
    preprocessed_df = interim_df
    preprocessed_df['StartTime'] = pd.to_datetime(preprocessed_df['StartTime'])

    preprocessed_df['Proto_Int'] = preprocessed_df['Proto'].map(proto_dict)
    preprocessed_df['Proto_Int'].fillna(proto_dict['Unknown'])
    preprocessed_df['Proto_Int'] = preprocessed_df['Proto_Int'].astype('category')

    preprocessed_df['Sport_Int'] = pd.cut(preprocessed_df['Sport'], bins=port_bins,
                                          labels=port_labels, include_lowest=True)
    preprocessed_df['Sport_Int'] = preprocessed_df['Sport_Int'].astype('category')

    preprocessed_df['Dir_Int'] = preprocessed_df['Dir'].map(dir_dict)
    preprocessed_df['Dir_Int'] = preprocessed_df['Dir_Int'].fillna(dir_dict['Unknown'])
    preprocessed_df['Dir_Int'] = preprocessed_df['Dir_Int'].astype('category')

    preprocessed_df['Dport_Int'] = pd.cut(preprocessed_df['Dport'], bins=port_bins,
                                          labels=port_labels, include_lowest=True)
    preprocessed_df['Dport_Int'] = preprocessed_df['Dport_Int'].astype('category')

    preprocessed_df['State_Int'] = preprocessed_df['State'].map(state_dict)
    preprocessed_df['State_Int'] = preprocessed_df['State_Int'].fillna(state_dict['Unknown'])
    preprocessed_df['State_Int'] = preprocessed_df['State_Int'].astype('category')

    preprocessed_df['is_fwd'] = preprocessed_df['Sport']
    preprocessed_df.loc[preprocessed_df['Sport'] >= 1024, 'is_fwd'] = 1
    preprocessed_df.loc[preprocessed_df['Sport'] < 1024, 'is_fwd'] = 0

    makedirs(dirname(preprocessed_output_path), exist_ok=True)
    preprocessed_df.to_csv(preprocessed_output_path, index=False)
