#!/usr/bin/python
'''This is a python program which is used to automate the process of
updating ioc JSON file with new api information, no new rows added'''
import argparse
import os.path as path
import pathlib
import sys
import datetime
import bulk_json_generator as generator
sys.path.append('../')
import utils.validator as validator
import utils.file_util as util

# Declaring globals
FILE_PATH = pathlib.Path(__file__).parent.absolute()
# Holds VT API information
CONFIG = util.load_yaml('{}/config.yml'.format(FILE_PATH))


def argparser():
    '''Parses the user arguments and checks path correct paths'''
    parser = argparse.ArgumentParser(
        description="Updating/Refreshing existing JSON latest API information")
    parser.add_argument('-path', '--path', required=True, dest='json_path', metavar='',
                        help='Path to bulk api JSON to be updated\
                            (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json',
                        action='store')

    args = parser.parse_args()
    # Checking validity pf paths
    if args.json_path and not path.exists(args.json_path):
        parser.error(f"The file {args.json_path} does not exist!")
    return args

def parse_bulk_api(file_path):
    '''
    Parse data into separate lists based on ioc_type returning a dict
    :param file_path: Path to existing bulk api
    :type file_path: str
    :return seperated_mapping: Returns a mapping of ket value pairs (ioc_type: values)
    :rtype domain_list: dict of (str, list)
    '''
    init_list = util.convert_to_json(file_path)
    # Removing duplicates
    ioc_list = generator.delete_duplicates(init_list, silent=True)
    md5_list, sha256_list, url_list, ip_list, domain_list, other_list = [], [], [], [], [], []
    seperated_mapping = {}
    for ioc in ioc_list:
        if ioc["type"] == "MD5":
            md5_list.append(ioc)
        elif ioc["type"] == "SHA256":
            sha256_list.append(ioc)
        elif ioc["type"] == "URL":
            url_list.append(ioc)
        elif ioc["type"] == "IP":
            ip_list.append(ioc)
        elif ioc["type"] == "DOMAIN":
            domain_list.append(ioc)
        else:
            other_list.append(ioc)
    seperated_mapping.update({'MD5': md5_list, 'SHA256': sha256_list, 'URL': url_list,
                              'IP': ip_list, 'DOMAIN': domain_list, 'OTHER': other_list})
    return seperated_mapping

def main():
    '''main'''
    args = argparser()
    ioc_file = args.json_path

    # Validating config file for API keys
    validator.is_valid_kibana_config(CONFIG, raise_error=True)
    start_time = datetime.datetime.now()
    print(f"{start_time} - Updating existing JSON, this may take a while...")
    # Parse the JSON into separate lists based on ioc types
    # May return a empty list for a certain ioc type
    parsed_json = parse_bulk_api(args.json_path)
    key_list = parsed_json.keys()
    updated_values = []
    # For each ioc type, call the appropriate apis
    for ioc in key_list:
        # Only update non null values
        if parsed_json[ioc]:
            updated_values.extend(generator.call_apis(parsed_json[ioc], ioc))
    util.write_bulk_api(updated_values, ioc_file)
    # Parse the source url
    final_values = generator.parse_url_dict(updated_values, 'source')

    # Overwriting file
    util.write_bulk_api(final_values, ioc_file)
    end_time = datetime.datetime.now()
    print(f"{end_time} - BulkAPI JSON Updated at: {ioc_file}")


if __name__ == "__main__":
    main()
