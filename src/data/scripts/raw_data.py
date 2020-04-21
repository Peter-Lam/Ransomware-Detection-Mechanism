#!/usr/bin/python
'''
    make_raw_data will create input.csv in project/data/raw/ directory
'''
import re
from os import listdir, makedirs
from os.path import dirname, isfile, join
import sys

#Global
CONFIG_PATH = './config.yml'

sys.path.append('../')
from utils.file_util import load_json, load_yaml

def main():
    ''' create input.csv in project/data/raw/ directory '''
    make_raw_data()

def make_raw_data():
    ''' create input.csv in project/data/raw/ directory '''
    config = load_yaml(CONFIG_PATH)
    binetflow_path = config['binet_output_path']
    raw_output_path = config['raw_output_path']
    dataset_path = config['dataset_path']
    dataset_json = load_json(dataset_path)
    dict_mal_hosts = dict_infected_hosts(dataset_json)
    file_list = get_file_list(binetflow_path)
    create_input_csv(file_list, binetflow_path, raw_output_path, dict_mal_hosts)

def get_file_list(binetflow_path):
    '''Returns a list of all files in the given directory path'''
    return [file for file in listdir(binetflow_path) if isfile(join(binetflow_path, file))]

def create_input_csv(file_list, dir_path, output_path, dict_mal_hosts):
    '''
        Parse through each binetflow file and append to a brand new file called input.csv.
        Some files have extra columns srcUdata,dstUdata.
        A solution is to put the table columns as ones including srcUdata,dstUdata and
        put null value in those columns in files without them.
    '''
    # Majority files have 15 columns
    default_len = 15
    if file_list:
        makedirs(dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as input_file:
            # Insert columns headers manually as some files have different columns
            input_file.write(('StartTime,Dur,Proto,SrcAddr,Sport,Dir,DstAddr,Dport,State,'
                              + 'sTos,dTos,TotPkts,TotBytes,SrcBytes,srcUdata,dstUdata,Label\n'))
            for file_name in file_list:
                with open(dir_path + '/' + file_name, 'r') as binet_file:
                    # Column Headers
                    line = binet_file.readline()
                    #First row
                    line = binet_file.readline()
                    while line:
                        row_l = line.split(',')
                        if len(row_l) == default_len:
                            # add columns for srcUdata and dstUdata
                            row_l.insert(len(row_l) - 1, '')
                            row_l.insert(len(row_l) - 1, '')
                        elif len(row_l) == 17:
                            # srcUdata
                            if row_l[-3]:
                                row_l[-3] = format_string(row_l[-3])
                            # dstUdata
                            if row_l[-2]:
                                row_l[-2] = format_string(row_l[-2])

                        elif len(row_l) > 17:
                            srcu_match = re.search(r's\[[0-9]*\].*', line) # Str from scru to label
                            dstu_match = re.search(r'd\[[0-9]*\].*', line) # Str from dstu to label

                            if srcu_match is not None and dstu_match is not None:
                                srcu = srcu_match.group(0)
                                dstu = dstu_match.group(0)

                                srcu = format_string(srcu[:srcu.find(dstu) - 1])
                                dstu = format_string(dstu[:(dstu.rfind(','))])
                                additions = [srcu, dstu, row_l[-1]]
                                row_l = row_l[:default_len - 1]
                                row_l.extend(additions)

                            elif srcu_match is not None:
                                srcu = srcu_match.group(0)
                                srcu = format_string(srcu[:srcu.rfind(row_l[-2]) - 1])
                                additions = [srcu, row_l[-2], row_l[-1]]
                                row_l = row_l[:default_len - 1]
                                row_l.extend(additions)

                            elif dstu_match is not None:
                                dstu = dstu_match.group(0)
                                dstu = format_string(dstu[:dstu.rfind(row_l[-1]) - 1])
                                additions = [dstu, row_l[-1]]
                                row_l = row_l[:default_len]
                                row_l.extend(additions)
                        row_l[-1] = str(int(row_l[3] in dict_mal_hosts[file_name]
                                            or row_l[6] in dict_mal_hosts[file_name])) + '\n'
                        line = ','.join(row_l) # Form row as a string
                        input_file.write(line) # Write line to input.csv
                        line = binet_file.readline() # Get Next row

def format_string(string):
    '''
        Format string to be read properly by pandas
        Escape quote is blackslash. String might contain backslash.
        Replace all backslashes with doubleslashes.
        String might have quotes.
        Replace all double quotes with blacksplash + quote
    '''
    string = string.replace("\\", "\\\\")
    string = string.replace("\"", "\\\"")
    return encapsulate_str(string)

def encapsulate_str(string):
    '''
        Encapsulates string with double quotes
    '''
    return  "\""+ string + "\""

def dict_infected_hosts(dataset_json):
    '''
        Iterates through the dataset_json file to
        make a dictionary with a key: file_name, value: ip
    '''
    dict_hosts = {}
    for data in dataset_json:
        file_name = data['source'].split('/')[-2] + '.csv'
        dict_hosts[file_name] = data['infected_host']
    return dict_hosts
