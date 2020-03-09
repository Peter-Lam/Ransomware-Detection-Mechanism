#!/usr/bin/python
'''
    This is a python program will create interim.csv
'''
import socket

from os import makedirs
from os.path import dirname
from utils.file_util import load_yaml

def main():
    '''main'''
    make_interim()

def make_interim():
    '''
        Read input.csv and remove rows null  {srcaddr, dstaddr, srcport, dstport}
    '''
    config = load_yaml('./config.yml')
    raw_output_path = config['raw_output_path']
    interim_output_path = config['interim_output_path']
    makedirs(dirname(interim_output_path), exist_ok=True)
    with open(raw_output_path, 'r') as input_file:
        with open(interim_output_path, 'w') as interim_file:
            line = input_file.readline()
            row_l = remove_srcu_dstu(line)
            interim_file.write(','.join(row_l))
            line = input_file.readline()
            while line:
                row_l = remove_srcu_dstu(line)
                if not mising_addr_info(row_l[3], row_l[4], row_l[6], row_l[7]):
                    try:
                        socket.inet_aton(row_l[3])
                        socket.inet_aton(row_l[6])
                        interim_file.write(','.join(row_l))
                    except OSError:
                        pass
                line = input_file.readline()

def mising_addr_info(src_addr, src_port, dst_addr, dst_port):
    '''
        Returns True if any of src address, src port, destination
        address, destination port is empty or not a number (ports)
    '''
    if not src_addr or not src_port or not dst_addr or not dst_port:
        return True
    if src_port and not src_port.isdigit():
        return True
    if dst_port and not dst_port.isdigit():
        return True
    return False

def remove_srcu_dstu(line):
    '''
        Removes the srcUdata and dstUdata as more than 90 rows are empty.
        Returns a copy of the new row
    '''
    default_len = 15
    full_row_list = line.split(',')
    tmp = full_row_list[-1]
    new_row_l = full_row_list[:default_len - 1]
    new_row_l.append(tmp)
    return new_row_l
