#!/usr/bin/python
'''
    This is the main file to create the features using the preprocessed.csv
'''

import pandas as pd

def main():
    '''
        Read the preprocessed.csv. Create feature:
        1. Total flows in the forward direction in the window 
    '''
    make_features()

def make_features():
    '''
        Call all the function to create features
    '''
    pre_df = pd.read_csv('../../data/preprocessed/preprocessed.csv')

    print(pre_df['StartTime'])

    # print(mean_duration_of_attack(pre_df))
    # print(mean_size_fwd_dir(pre_df))

def mean_duration_of_attack(df): 
    return df['Dur'].sum()

'''Mean size of flow in forward direction in the window'''
def mean_size_fwd_dir(df):
    test = df.loc[df['Dir'].str.strip()=="->'"]
    

if __name__ == '__main__':
    main()