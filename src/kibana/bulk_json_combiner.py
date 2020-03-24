#!/usr/bin/python
'''This is a python program which is used to combine two existing bulk API jsons into a new file'''
import argparse
import os.path as path
import sys
import datetime
from distutils.util import strtobool
import bulk_json_generator as generator
sys.path.append('../')
import utils.file_util as util

def argparser():
    '''File parser for arguments'''
    parser = argparse.ArgumentParser(
        description="Combining two ioc json files together")
    parser.add_argument('-a', '--file_1', required=True, dest='json_1', metavar='',
                        help='Path to first bulk api JSON to be combined\
                              (e.g. ../Ransomware-Detection-Mechanism/ioc_list.json',
                        action='store')
    parser.add_argument('-b', '--file_2', required=True, dest='json_2', metavar='',
                        help='Path to second bulk api JSON to be combined\
                            (e.g. ../Ransomware-Detection-Mechanism/ioc_list.json',
                        action='store')
    parser.add_argument('-dest', '--dest', required=False, dest='dest', metavar='',
                        help='Destination of combined file, if this argument is not used,\
                              the second file will be combined on the first file --\
                              (e.g. ../Ransomware-Detection-Mechanism/ioc_list.json',
                        action='store')
    args = parser.parse_args()
    # Checking validity pf paths
    if args.json_1 and not path.exists(args.json_1):
        parser.error(f"The file {args.json_1} does not exist!")
    if args.json_2 and not path.exists(args.json_2):
        parser.error(f"The file {args.json_2} does not exist!")
    if args.dest and path.exists(args.dest):
        answer = input(f"The destination already exists at: {args.dest}\
                        \nWould you like to overwrite (Y/N)?")
        try:
            if strtobool(answer):
                print("Overwriting existing file...")
            else:
                parser.error("Please try again and choose another path")
        except ValueError:
            parser.error("Invalid answer, please select 'Y' or 'N' next time")
    return args

def main(args):
    '''main'''
    # Setting variaables
    json_path_1 = args.json_1
    json_path_2 = args.json_2

    if args.dest:
        print(f"Combining files and writing to {args.dest}...")
    else:
        print(f"Combining files onto {json_path_1}...")

    # Reading files and deleting duplicates
    init_list = util.convert_to_json(json_path_1)
    ioc_list = generator.delete_duplicates(init_list, silent=True)
    # Reading second json and checking against the first for duplicates
    init_list_2 = util.convert_to_json(json_path_2)
    ioc_list_2 = generator.delete_duplicates(init_list_2, second_list=ioc_list, silent=True)
    # Combining lists
    final_ioc_list = ioc_list
    final_ioc_list.extend(ioc_list_2)

    end_time = datetime.datetime.now()
    # Writing to files
    if args.dest:
        util.write_bulk_api(final_ioc_list, args.dest)
        print(f"{end_time} - New file has been created at: {args.dest}")
    else:
        util.write_bulk_api(final_ioc_list, json_path_1)
        print(f"{end_time} - BulkAPI JSON Updated at: {json_path_1}")

if __name__ == "__main__":
    ARGS = argparser()
    main(ARGS)
