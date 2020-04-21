#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    This is the main file to making and engineering features.
'''

from os import makedirs
from os.path import dirname

import math
import sys
import time
import numpy as np
import pandas as pd

sys.path.append('../')
from utils.file_util import load_yaml

#Global
CONFIG_PATH = './features_config.yml'

def main():
    """
        Retrieves an already preprocessed version of the dataset.
        The final CSV will be sorted on StartTime.
        Build DstBytes
        Build features based on the following:
            Total flows in the forward direction in the window
            Total flows in the backward direction in the window
            Total size of netflows in forward direction in the window
            Total size of netflows in backward direction in the window
            Minimum size of flow in forward direction in the window
            Minimum size of flow in backward direction in the window
            Maximum size of flow in forward direction in the window
            Maximum size of flow in backward direction in the window
            Mean size of flow in forward direction in the window
            Mean size of flow in backward direction in the window
            Standard Deviation size of flow in forward direction in the window
            Standard Deviation size of flow in backward direction in the window
            Time between 2 flows in the window in the forward direction
            Time between 2 flows in the window in the backward direction
        A similar approach is down on TotBytes, TotPkts, SrcBytes.
        Window is 10k elements and 10 Minutes.
        This window is done again with focus on source and destination addresses
        A sample containing the first 50 rows will be saved.
        A new CSV with raw + discretized + engineered will be saved.
    """
    start = time.time()
    config = load_yaml(CONFIG_PATH)
    preprocessed_path = config['preprocessed_path']
    processed_output_path = config['processed_path']
    sample_output_path = config['sample_processed_path']
    sample_size = config['sample_size']
    #Window for N elements
    num_window_size = config['num_window_size']
    minutes_window_size = config['minutes_window_size']
    pd_roll_time_size = config['pd_roll_time_size']
    feature_df = pd.read_csv(preprocessed_path)
    feature_df['StartTime'] = pd.to_datetime(feature_df['StartTime'])
    feature_df = feature_df.sort_values('StartTime').reset_index(drop=True)
    feature_df['epoch'] = ((feature_df['StartTime'] - pd.Timestamp('1970-01-01'))
                           // pd.Timedelta('1ms')) / 1000
    #Roughly 191 extra columns should be added

    #Bytes
    feature_df['DstBytes'] = feature_df['TotBytes'] - feature_df['SrcBytes']

    print(f'Building Total Flow in {minutes_window_size} minutes')
    build_gen_total_flows(feature_df, pd_roll_time_size)

    print(f'Building Total Flow in on SrcAddr and DstAddr in minutes and num elements')
    build_addr_total_flows(feature_df, 'SrcAddr', pd_roll_time_size)
    build_addr_total_flows(feature_df, 'DstAddr', pd_roll_time_size)
    build_addr_total_flows(feature_df, 'SrcAddr', num_window_size)
    build_addr_total_flows(feature_df, 'DstAddr', num_window_size)

    print(f'Building Time Between 2 Flows with {minutes_window_size} minutes')
    feature_df = build_time_between_2_flow_time(feature_df, minutes_window_size)
    print(f'Building Time Between 2 Flows with {num_window_size} elements')
    feature_df = build_time_between_2_flow_num(feature_df, num_window_size)

    print(f'Building TotBytes, TotPkts, SrcBytes, metrics in {minutes_window_size} minutes')
    build_gen_features(feature_df, 'TotBytes', pd_roll_time_size)
    build_gen_features(feature_df, 'TotPkts', pd_roll_time_size)
    build_gen_features(feature_df, 'SrcBytes', pd_roll_time_size)

    print(f'Building TotBytes, TotPkts, SrcBytes with {minutes_window_size} minutes on SrcAddr')
    build_addr_features(feature_df, 'SrcAddr', 'TotBytes', pd_roll_time_size)
    build_addr_features(feature_df, 'SrcAddr', 'TotPkts', pd_roll_time_size)
    build_addr_features(feature_df, 'SrcAddr', 'SrcBytes', pd_roll_time_size)

    print(f'Building TotBytes, TotPkts, SrcBytes with {minutes_window_size} minutes on DstAddr')
    build_addr_features(feature_df, 'DstAddr', 'TotBytes', pd_roll_time_size)
    build_addr_features(feature_df, 'DstAddr', 'TotPkts', pd_roll_time_size)
    build_addr_features(feature_df, 'DstAddr', 'SrcBytes', pd_roll_time_size)

    print(f'Building TotBytes, TotPkts, SrcBytes with {num_window_size} elements on Src and Dst')
    build_addr_features(feature_df, 'SrcAddr', 'TotBytes', num_window_size)
    build_addr_features(feature_df, 'SrcAddr', 'TotPkts', num_window_size)
    build_addr_features(feature_df, 'SrcAddr', 'SrcBytes', num_window_size)
    build_addr_features(feature_df, 'DstAddr', 'TotBytes', num_window_size)
    build_addr_features(feature_df, 'DstAddr', 'TotPkts', num_window_size)
    build_addr_features(feature_df, 'DstAddr', 'SrcBytes', num_window_size)

    #Write Sample to CSV
    makedirs(dirname(processed_output_path), exist_ok=True)
    feature_df.drop(columns=['epoch'], inplace=True, axis=1)
    feature_df.head(sample_size).to_csv(sample_output_path, index=False)
    #Write Raw and Features to CSV file.
    feature_df.to_csv(processed_output_path, index=False)
    print(time.time() - start)

def addr_prefix(addr):
    '''
        Returns (String)
        Returns S if addr is SrcAddr
        Returns D if addr is DstAddr
    '''
    if addr == 'SrcAddr':
        return 'S'
    if addr == 'DstAddr':
        return 'D'
    return ''

def roll_suffix(window):
    '''
        Returns (String)
        Returns '' if window is a string
        Returns N if window is not a string
    '''
    return '' if isinstance(window, str) else 'N'

def dir_infix(is_fwd):
    '''
        Returns (String)
        Returns Fwd if is_fwd is True
        Returns Bwd if is_fwd is False
    '''
    return 'Fwd' if is_fwd else 'Bwd'

def split_list_chunks(lst, size_per_chunk):
    '''
        Splits list equally with chuncks of size n
    '''
    for i in range(0, len(lst), size_per_chunk):
        yield lst[i:i + size_per_chunk]

def calc_flow_diff_range(epoch_list, window_range_sec):
    '''
        If there is 2 items, calculate the time difference if it is
        less than window range sec.
        Return difference.
    '''
    if len(epoch_list) < 2 or (epoch_list[-1] - epoch_list[-2]) > window_range_sec:
        return 0
    return epoch_list[-1] - epoch_list[-2]

def calc_flow_diff_index(index_epoch_l, window_size):
    '''
        Each item in the list is a list of size 2 containing index and epoch.
        If there is 2 items, calculate the time difference if it is
        the indexes are n rows apart.
        Return difference.
    '''
    if len(index_epoch_l) < 2 or (index_epoch_l[-1][0] - index_epoch_l[-2][0]) > window_size:
        return 0
    return index_epoch_l[-1][1] - index_epoch_l[-2][1]

def trim_dict_value_list(key, dictionary, size):
    '''
        Assumes the value of the dictionary is a list.
        If list exceeds size. Pop until list conforms with size.
        If key does not exist. Create a key value pair with empty list.
    '''
    if key in dictionary:
        while len(dictionary[key]) >= size:
            dictionary[key].pop(0)
    else:
        dictionary[key] = []

def print_status(index, total, percentage=5):
    '''
        Prints the number of iterations before
        a loop is completed given an index, total len
        of loop, and percentage.
    '''
    threshold = math.ceil(total*(percentage/100))
    if index % threshold == 0:
        completion = index/total * 100
        print(f'TASK: {completion}% Completed')

def create_rolling_obj(f_df, roll_cols, window):
    '''
        Creates a pandas rolling object given window and columns on dataframe.
        Min periods is automatically set to 0.
    '''
    return f_df[roll_cols].rolling(window, min_periods=1, on='StartTime')

def build_addr_features(f_df, addr, col, window):
    '''
        Builds the sum, min, max, mean, std for a column
        in a integer or time window in both fwd and bwd direction
        focusing on the Src or Dst addresses.
    '''
    _build_addr_features(f_df, addr, col, window, 1)
    _build_addr_features(f_df, addr, col, window, 0)

def _build_addr_features(f_df, addr, col, window, is_fwd): # pylint: disable=R0914
    '''
        Helper to build_addr_features
    '''
    prefix = addr_prefix(addr)
    suffix = roll_suffix(window)
    is_fwd_infix = dir_infix(is_fwd)

    data_f = f_df[['StartTime', addr, col, 'is_fwd']].copy()
    #Make null values not in the given direction
    data_f.loc[data_f.is_fwd != is_fwd, col] = np.NaN

    sum_name = f'{prefix}{col}Sum{is_fwd_infix}_{window}{suffix}'
    min_name = f'{prefix}{col}Min{is_fwd_infix}_{window}{suffix}'
    max_name = f'{prefix}{col}Max{is_fwd_infix}_{window}{suffix}'
    mean_name = f'{prefix}{col}Mean{is_fwd_infix}_{window}{suffix}'
    std_name = f'{prefix}{col}Std{is_fwd_infix}_{window}{suffix}'

    f_df[sum_name] = np.NaN
    f_df[min_name] = np.NaN
    f_df[max_name] = np.NaN
    f_df[mean_name] = np.NaN
    f_df[std_name] = np.NaN

    #Make the addr columns
    all_addrs = data_f[addr].unique().tolist()
    split_addr_list = list(split_list_chunks(all_addrs, 100))
    for chunk in split_addr_list:
        addr_df = data_f.copy()
        for ip_v4 in chunk:
            addr_df[ip_v4] = np.NaN
            addr_df.loc[addr_df[addr] == ip_v4, ip_v4] = addr_df[col]

        roll_obj = create_rolling_obj(addr_df, ['StartTime'] + chunk, window)
        del addr_df
        #Sum
        rolled_df = roll_obj.sum()
        rolled_df[addr] = data_f[addr]
        for ip_v4 in chunk:
            f_df.loc[f_df[addr] == ip_v4, sum_name] = rolled_df.loc[rolled_df[addr] == ip_v4][ip_v4]
        #Min
        rolled_df = roll_obj.min()
        rolled_df[addr] = data_f[addr]
        for ip_v4 in chunk:
            f_df.loc[f_df[addr] == ip_v4, min_name] = rolled_df.loc[rolled_df[addr] == ip_v4][ip_v4]
        #Max
        rolled_df = roll_obj.max()
        rolled_df[addr] = data_f[addr]
        for ip_v4 in chunk:
            f_df.loc[f_df[addr] == ip_v4, max_name] = rolled_df.loc[rolled_df[addr] == ip_v4][ip_v4]
        #Mean
        rolled_df = roll_obj.mean()
        rolled_df[addr] = data_f[addr]
        for ip_4 in chunk:
            f_df.loc[f_df[addr] == ip_4, mean_name] = rolled_df.loc[rolled_df[addr] == ip_4][ip_4]
        #Std
        rolled_df = roll_obj.std(ddof=0)
        rolled_df[addr] = data_f[addr]
        for ip_v4 in chunk:
            f_df.loc[f_df[addr] == ip_v4, std_name] = rolled_df.loc[rolled_df[addr] == ip_v4][ip_v4]
        del roll_obj
        del rolled_df

    f_df[sum_name] = f_df[sum_name].fillna(0)
    f_df[min_name] = f_df[min_name].fillna(0)
    f_df[max_name] = f_df[max_name].fillna(0)
    f_df[mean_name] = f_df[mean_name].fillna(0)
    f_df[std_name] = f_df[std_name].fillna(0)
    f_df[sum_name] = f_df[sum_name].astype('int64')
    f_df[min_name] = f_df[min_name].astype('int64')
    f_df[max_name] = f_df[max_name].astype('int64')

def build_addr_total_flows(f_df, addr, window):
    '''
        Builds the total flows forward and backward
        given a integer or time window and
        given whether depenent on src or dst addr.
    '''
    _build_addr_total_flows(f_df, addr, window, 1)
    _build_addr_total_flows(f_df, addr, window, 0)

def _build_addr_total_flows(f_df, addr, window, is_fwd):
    '''
        Helper function to build_addr_total_flows
    '''
    is_fwd_infix = dir_infix(is_fwd)

    data_f = f_df[['StartTime', addr, 'is_fwd']].copy()
    if not is_fwd:
        data_f.is_fwd = data_f.is_fwd.replace({0:1, 1:0})

    col_name = f'{addr_prefix(addr)}TotalFlow{is_fwd_infix}_{window}{roll_suffix(window)}'
    f_df[col_name] = np.NaN

    all_addrs = data_f[addr].unique().tolist()
    split_addr_list = list(split_list_chunks(all_addrs, 100))
    for chunk in split_addr_list:
        addr_df = data_f.copy()
        for ip_v4 in chunk:
            addr_df[ip_v4] = np.NaN
            addr_df.loc[addr_df[addr] == ip_v4, ip_v4] = addr_df.is_fwd
        roll_obj = create_rolling_obj(addr_df, ['StartTime'] + chunk, window)
        del addr_df
        rolled_df = roll_obj.sum()
        rolled_df[addr] = data_f[addr]
        for ip_4 in chunk:
            f_df.loc[f_df[addr] == ip_4, col_name] = rolled_df.loc[rolled_df[addr] == ip_4][ip_4]
        del roll_obj
        del rolled_df
    f_df[col_name] = f_df[col_name].fillna(0)
    f_df[col_name] = f_df[col_name].astype('int64')

def build_gen_features(f_df, col, window):
    '''
        Builds the sum, min, max, mean, std for a column
        in a integer or time window in both fwd and bwd direction.
    '''
    _build_gen_features(f_df, col, window, 1)
    _build_gen_features(f_df, col, window, 0)

def _build_gen_features(f_df, col, window, is_fwd):
    '''
        Helper to _build_gen_features
    '''
    suffix = roll_suffix(window)
    is_fwd_infix = dir_infix(is_fwd)

    data_f = f_df[['StartTime', col, 'is_fwd']].copy()
    #Make null values not in the given direction
    data_f.loc[data_f.is_fwd != is_fwd, col] = np.NaN
    roll_cols = ['StartTime', col]
    roll_df = create_rolling_obj(data_f, roll_cols, window)

    sum_name = f'{col}Sum{is_fwd_infix}_{window}{suffix}'
    min_name = f'{col}Min{is_fwd_infix}_{window}{suffix}'
    max_name = f'{col}Max{is_fwd_infix}_{window}{suffix}'
    mean_name = f'{col}Mean{is_fwd_infix}_{window}{suffix}'
    std_name = f'{col}Std{is_fwd_infix}_{window}{suffix}'

    f_df[sum_name] = roll_df.sum()[col]
    f_df[min_name] = roll_df.min()[col]
    f_df[max_name] = roll_df.max()[col]
    f_df[mean_name] = roll_df.mean()[col]
    f_df[std_name] = roll_df.std(ddof=0)[col]
    f_df[sum_name] = f_df[sum_name].fillna(0)
    f_df[min_name] = f_df[min_name].fillna(0)
    f_df[max_name] = f_df[max_name].fillna(0)
    f_df[mean_name] = f_df[mean_name].fillna(0)
    f_df[std_name] = f_df[std_name].fillna(0)
    f_df[sum_name] = f_df[sum_name].astype('int64')
    f_df[min_name] = f_df[min_name].astype('int64')
    f_df[max_name] = f_df[max_name].astype('int64')

def build_gen_total_flows(f_df, window):
    '''
        Builds the total flows forward and backward
        given a integer or time window.
        Independent from the rows src or dst address
    '''
    _build_gen_total_flows(f_df, window, 1)
    _build_gen_total_flows(f_df, window, 0)

def _build_gen_total_flows(f_df, window, is_fwd):
    '''
        Helper function to build_gen_total_flows
    '''
    suffix = roll_suffix(window)
    is_fwd_infix = dir_infix(is_fwd)

    data_f = f_df[['StartTime', 'is_fwd']].copy()
    if not is_fwd:
        data_f.is_fwd = data_f.is_fwd.replace({0:1, 1:0})
    roll_cols = ['StartTime', 'is_fwd']
    total_flow_df = create_rolling_obj(data_f, roll_cols, window).sum()
    col_name = f'TotalFlow{is_fwd_infix}_{window}{suffix}'
    f_df[col_name] = total_flow_df['is_fwd']

def build_time_between_2_flow_time(f_df, minutes):
    '''
        Given Dataframe and Minutes, Creates a new columns with
        the time between 2 flows in time window for both SrcAddr and DstAddr
    '''
    data_f = f_df[['SrcAddr', 'DstAddr', 'is_fwd', 'epoch']].copy()
    window_range_sec = minutes * 60

    src_fwd_dict = {}
    src_bwd_dict = {}
    dst_fwd_dict = {}
    dst_bwd_dict = {}

    #Time Between Flows
    src_fwd_list = []
    src_bwd_list = []

    dst_fwd_list = []
    dst_bwd_list = []

    for index, row in data_f.iterrows():
        print_status(index, len(data_f.index))
        if row.is_fwd:
            trim_dict_value_list(row.SrcAddr, src_fwd_dict, 2)
            trim_dict_value_list(row.DstAddr, dst_fwd_dict, 2)

            src_fwd_dict[row.SrcAddr].append(row.epoch)
            dst_fwd_dict[row.DstAddr].append(row.epoch)

            src_bwd_list.append(0)
            dst_bwd_list.append(0)

            #Forward Src
            src_fwd_list.append(calc_flow_diff_range(src_fwd_dict[row.SrcAddr], window_range_sec))
            #Forward Dst
            dst_fwd_list.append(calc_flow_diff_range(dst_fwd_dict[row.DstAddr], window_range_sec))
        else:
            trim_dict_value_list(row.SrcAddr, src_bwd_dict, 2)
            trim_dict_value_list(row.DstAddr, dst_bwd_dict, 2)

            src_bwd_dict[row.SrcAddr].append(row.epoch)
            dst_bwd_dict[row.DstAddr].append(row.epoch)

            src_fwd_list.append(0)
            dst_fwd_list.append(0)

            #Backward Src
            src_bwd_list.append(calc_flow_diff_range(src_bwd_dict[row.SrcAddr], window_range_sec))
            #Backward Dst
            dst_bwd_list.append(calc_flow_diff_range(dst_bwd_dict[row.DstAddr], window_range_sec))
    #Build Data Frame
    new_features_df = pd.DataFrame(data={
        f'STimeBetween2FlowFwd_{minutes}T': src_fwd_list,
        f'STimeBetween2FlowBwd_{minutes}T': src_bwd_list,
        f'DTimeBetween2FlowFwd_{minutes}T': dst_fwd_list,
        f'DTimeBetween2FlowBwd_{minutes}T': dst_bwd_list
    })
    return pd.concat([f_df, new_features_df], axis=1)

def build_time_between_2_flow_num(f_df, window_size):
    '''
        Given Dataframe and Minutes, Creates a new columns with
        the time between 2 flows in num window for both SrcAddr and DstAddr
    '''
    data_f = f_df[['SrcAddr', 'DstAddr', 'is_fwd', 'epoch']].copy()
    total = len(data_f.index)

    src_fwd_dict = {}
    src_bwd_dict = {}
    dst_fwd_dict = {}
    dst_bwd_dict = {}

    #Time Between Flows
    src_fwd_list = []
    src_bwd_list = []

    dst_fwd_list = []
    dst_bwd_list = []

    for index, row in data_f.iterrows():
        print_status(index, total)
        if row.is_fwd:
            trim_dict_value_list(row.SrcAddr, src_fwd_dict, 2)
            trim_dict_value_list(row.DstAddr, dst_fwd_dict, 2)

            src_fwd_dict[row.SrcAddr].append([index, row.epoch])
            dst_fwd_dict[row.DstAddr].append([index, row.epoch])

            src_bwd_list.append(0)
            dst_bwd_list.append(0)

            #Forward Src
            src_fwd_list.append(calc_flow_diff_index(src_fwd_dict[row.SrcAddr], window_size))
            #Forward Dst
            dst_fwd_list.append(calc_flow_diff_index(dst_fwd_dict[row.DstAddr], window_size))
        else:
            trim_dict_value_list(row.SrcAddr, src_bwd_dict, 2)
            trim_dict_value_list(row.DstAddr, dst_bwd_dict, 2)

            src_bwd_dict[row.SrcAddr].append([index, row.epoch])
            dst_bwd_dict[row.DstAddr].append([index, row.epoch])

            src_fwd_list.append(0)
            dst_fwd_list.append(0)

            #Backward Src
            src_bwd_list.append(calc_flow_diff_index(src_bwd_dict[row.SrcAddr], window_size))
            #Backward Dst
            dst_bwd_list.append(calc_flow_diff_index(dst_bwd_dict[row.DstAddr], window_size))
    #Build Data Frame
    new_features_df = pd.DataFrame(data={
        f'STimeBetween2FlowFwd_{window_size}N': src_fwd_list,
        f'STimeBetween2FlowBwd_{window_size}N': src_bwd_list,
        f'DTimeBetween2FlowFwd_{window_size}N': dst_fwd_list,
        f'DTimeBetween2FlowBwd_{window_size}N': dst_bwd_list
    })
    return pd.concat([f_df, new_features_df], axis=1)

if __name__ == '__main__':
    main()
