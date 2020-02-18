#!/usr/bin/python
'''
    This is a python program will create preproccesed.csv
'''

import numpy as np
import pandas as pd
import matplotlib
from pandas_profiling import ProfileReport

def main():
    '''
        By Default, Minimal Report is True.
        For correlation, check to False. (TO DOC)
        Run src/data/make_dataset.py before this script.
    '''
    matplotlib.use('Agg')
    interim_output_path = '../../data/interim/interim.csv'
    preprocessed_output_path = '../../data/preprocessed/preprocessed.csv'
    report_base_path = '../../reports'
    minimal_report = True

    create_report_interim(csv_to_df(interim_output_path), minimal_report, report_base_path)
    create_report_preprocessed(csv_to_df(preprocessed_output_path),
                               minimal_report,
                               report_base_path)

def create_report_interim(data_f, minimal_report, out_path):
    '''
        Creates a Profilng Report with the interim.csv
        but with addition configuration of sTos, dTos
        values be replaced with -1 if empty string.
    '''
    data_f['StartTime'] = pd.to_datetime(data_f['StartTime'])
    data_f.loc[data_f['sTos'].replace('', np.nan).isnull(), 'sTos'] = -1
    data_f.loc[data_f['dTos'].replace('', np.nan).isnull(), 'dTos'] = -1
    profile = ProfileReport(data_f,
                            minimal=minimal_report,
                            title='Full Interim Profiling Report (With Skew)',
                            html={'style':{'full_width':True}})
    output_file = '%s/%s_interim_report.html' % (out_path, type_of_report(minimal_report))
    profile.to_file(output_file=output_file)

def create_report_preprocessed(data_f, minimal_report, out_path):
    '''
        Creates a Profiling Report with preprocessed.csv
    '''
    data_f['StartTime'] = pd.to_datetime(data_f['StartTime'])
    profile = ProfileReport(data_f,
                            minimal=minimal_report,
                            title='Full Pre-Processed Profiling Report (No Skew)',
                            html={'style':{'full_width':True}})
    output_file = '%s/%s_processed_report.html' % (out_path, type_of_report(minimal_report))
    profile.to_file(output_file=output_file)

def csv_to_df(file_path):
    '''Given path, reads CSV and returns its data frame'''
    return pd.read_csv(file_path)

def type_of_report(minimal_report):
    '''If minimal is True then it is a min profiling, otherwise full'''
    return 'min' if minimal_report else 'full'

if __name__ == '__main__':
    main()

# def others():
#     quantile_list = [0, .125, .25, .375, .5, .625, .75, .875, 1.]
#     labels = [1, 2, 3, 4, 5, 6, 7, 8]

    # for col in ['State', 'Dir', 'Proto', 'Label']:
    #     df[col] = df[col].astype('category')

    # df.set_index('StartTime')
    # df['StartTime'] = df['StartTime'].apply(lambda x: x[:19])

    # bins_src_port = df['Sport'].quantile(quantile_list)
    # df['Sport'] = pd.cut(df['Sport'], bins=bins_src_port, labels=labels, include_lowest=True)

    # bins_dst_port = df['Dport'].quantile([0, .5, 1.])
    # df['Dport'] = pd.cut(df['Dport'], bins=bins_src_port, labels=labels, include_lowest=True)

    # for col in ['Sport', 'Dport']:
    #     df[col] = df[col].astype('int64')

    # df_new = df.copy()
    # for col in ['TotPkts', 'TotBytes', 'SrcBytes']:
    #     df_new[col] = np.log((1 + df_new[col]))
