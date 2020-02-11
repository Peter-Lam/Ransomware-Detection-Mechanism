#!/usr/bin/python
'''
    make_raw_data will create input.csv in project/data/raw/ directory
'''

from os import listdir, makedirs
from os.path import dirname, isfile, join
from utils.file_util import load_yaml

def main():
    ''' create input.csv in project/data/raw/ directory '''
    make_raw_data()

def make_raw_data():
    ''' create input.csv in project/data/raw/ directory '''
    config = load_yaml('./config.yml')
    binetflow_path = config['binet_output_path']
    raw_output_path = config['raw_output_path']
    file_list = get_file_list(binetflow_path)
    create_input_csv(file_list, binetflow_path, raw_output_path)

def get_file_list(binetflow_path):
    '''Returns a list of all files in the given directory path'''
    return [file for file in listdir(binetflow_path) if isfile(join(binetflow_path, file))]

def create_input_csv(file_list, dir_path, output_path):
    '''
        Parse through each binetflow file and append to a brand new file called input.csv.
        Some files have extra columns srcUdata,dstUdata.
        A solution is to put the table columns as ones including srcUdata,dstUdata and
        put null value in those columns in files without them.
    '''
    if file_list:
        makedirs(dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as input_file:
            col_str = ('StartTime,Dur,Proto,SrcAddr,Sport,Dir,DstAddr,Dport,State,'
                       + 'sTos,dTos,TotPkts,TotBytes,SrcBytes,srcUdata,dstUdata,Label\n')
            input_file.write(col_str)
            for file_name in file_list:
                path = dir_path + '/' + file_name
                with open(path, 'r') as binet_file:
                    line = binet_file.readline()
                    col = line.split(',')
                    col_size = len(col)
                    line = binet_file.readline()
                    while line:
                        if col_size == 15:
                            row_list = line.split(',')
                            row_list.insert(len(row_list)-1, '')
                            row_list.insert(len(row_list)-1, '')
                            line = ','.join(row_list)
                        input_file.write(line)
                        line = binet_file.readline()
