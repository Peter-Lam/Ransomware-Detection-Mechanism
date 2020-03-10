#!/usr/bin/python
'''This is a python program which is used to automate the process of
updating ioc JSON file with the appropriate values'''

import argparse
import os.path as path
import pathlib
import sys
import socket
import json
from distutils.util import strtobool
from urllib.parse import urlparse
sys.path.append('../')
from ip_info_service import ip_info_service
import update_virus_total_data as vt_updater
import json_translator as translator
import utils.file_util as util
# Declaring globals
FILE_PATH = pathlib.Path(__file__).parent.absolute()
# Holds VT API information
CONFIG = util.load_yaml('{}/config.yml'.format(FILE_PATH.parent))


def argparser():
    '''Parses the user arguments and checks path correct paths'''
    parser = argparse.ArgumentParser(
        description="update_json - Updating existing json files with more datasets")
    # Making new file and update file mutually exclusive options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-new', '--new', dest='new_path', metavar='',
                       help='writes to the full path of desired json file\
                            (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json',
                       action='store')
    group.add_argument('-update', '--update', dest='existing_path', metavar='',
                       help='updates the existing BULK api json file\
                            (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json',
                       action='store')
    parser.add_argument('-text', '--text', dest='values_path', metavar='',
                        required=True, help='text file containing values of the iocs',
                        action='store')
    parser.add_argument('-malware', '--malware', dest='malware', metavar='',
                        required=True, help='type of malware (e.g. Trickbot)', action='store')
    parser.add_argument('-ioc', '--ioc_type', type=str.upper, dest='ioc', nargs=1,
                        choices=['MD5', 'SHA256', 'IP',
                                 'URL', 'DOMAIN', 'other'],
                        metavar='', required=True,
                        help='type of ioc (MD5|SHA256|IP|URL|DOMAIN|other)',
                        action='store')
    parser.add_argument('-src', '--source', dest='source', metavar='', required=True,
                        help='Source of malware dataset(e.g. www.virusshare.com)',
                        action='store')
    args = parser.parse_args()
    # Checking validity pf paths
    if args.existing_path and not path.exists(args.existing_path):
        parser.error("The file %s does not exist!" % args.existing_path)
    if args.new_path and path.exists(args.new_path):
        answer = input(
            "The destination path already exists at: \
             %s\nWould you like to overwrite (Y/N)? " % args.new_path)
        try:
            if strtobool(answer):
                print("Overwriting existing file")
            else:
                parser.error("Please choose another path")
        except ValueError:
            parser.error("Invalid answer, please select 'Y' or 'N' next time")

    if not path.exists(args.values_path):
        parser.error("The file %s does not exist!" % args.values_path)
    return args


def is_valid_ip(value):
    '''Validating ip'''
    try:
        socket.inet_aton(value)
        return True
    except socket.error:
        # Not legal
        print(f"The following ip is not valid, skipping: {value}")
        return False


def is_valid_md5(value):
    '''Validating hash'''
    if len(value) == 32:
        return True
    print(
        f"The following MD5 is not the proper format: {value},\
            did you mean another hash type? ")
    return False


def is_valid_sha256(value):
    '''Validating hash'''
    if len(value) == 64:
        return True
    print(
        f"The following SHA256 is not the proper format: {value},\
            did you mean another hash type? ")
    return False


def parse_url_list(url_list):
    '''Breaking URL for query, path, filename, domain'''
    for url_dict in url_list:
        url = url_dict['value'].replace('[', '').replace(']', '').strip()
        if "://" not in url:
            url = f"http://{url}"
            parsed = urlparse(url)
            url_scheme = None
        else:
            parsed = urlparse(url)
            url_scheme = parsed.scheme
        url_query = parsed.query
        url_path = parsed.path
        url_domain = parsed.netloc
        url_hostname = parsed.hostname
        url_filename = pathlib.Path(url).stem
        url_file_ext = pathlib.Path(url).suffix
        if url_file_ext in url_filename or url_file_ext in url_domain:
            url_file_ext = ""
        if url_file_ext == "":
            url_filename = ""

        url_dict.update({'url_query': url_query,
                         'url_path': url_path,
                         'url_filename': url_filename,
                         'url_file_ext': url_file_ext,
                         'url_scheme': url_scheme,
                         'url_hostname': url_hostname,
                         'url_domain': url_domain})
    return url_list

def call_apis(list_values, ioc_type):
    '''Calling VT and IPInfor APIS and updating values'''
    if len(list_values) == 0:
        print("No valid values found, closing program")
        sys.exit()
    if ioc_type in ('MD5', 'SHA256'):
        print("Populating hash information from Virus Total...")
        updated_values = vt_updater.populate_hash(
            list_values, CONFIG['vt_report'], CONFIG['api_limit'])
    elif ioc_type == 'IP':
        print("Populating ip information  from Virus Total...")
        vt_updated_values = vt_updater.populate_ip(
            list_values, CONFIG['vt_ip'])
        print("Propulating ip information from IPInfo")
        updated_values = ip_info_service(CONFIG['ip_api'], vt_updated_values)
    elif ioc_type in ('URL', 'DOMAIN'):
        print("Populating domain information from Virus Total...")
        # updated_values = vt_updater.populate_domain(
        # base_info, CONFIG['vt_domain'])
        if ioc_type == 'URL':
            updated_values = parse_url_list(list_values)
    else:
        updated_values = list_values
    return updated_values
def main():
    '''main'''
    args = argparser()
    # Declaring variables
    ioc_type = (args.ioc)[0]
    list_to_push, list_values, base_info = [], [], []
    current_index = None
    # If --update was chosen then set appropriate values
    if args.existing_path:
        ioc_file = args.existing_path
        is_new_file = False
    else:
        ioc_file = args.new_path
        is_new_file = True

    # Read text file and grabbing a list of values
    list_values = util.load_file(args.values_path)

    # Loop through and add basic ioc information from args
    for value in list_values:
        # Only remove [] from IP but not others, like urls and domain to prevent accidental clicks
        if ioc_type == 'IP':
            resource = value.replace('[', '').replace(']', '').strip()
            # If the ip is not valid then skipping
            if not is_valid_ip(resource):
                continue
        else:
            resource = value.strip()
            if ioc_type == 'MD5' and not is_valid_md5(resource):
                continue
            if ioc_type == 'SHA256' and not is_valid_sha256(resource):
                continue
        base_info.append({'type': ioc_type, 'value': resource,
                          'malware': (args.malware).lower(), 'source': args.source})

    # Call Virus Total and IPInfo API to get missing data
    updated_values = call_apis(base_info, ioc_type)

    # If its a new file, then create and write to a new file
    if is_new_file:
        # Creating a temporary json and then converting to bulk api format
        util.write_json(
            updated_values, '{}/inputs/temp.json'.format(FILE_PATH.parent))
        translator.convert_to_bulk_api('{}/inputs/temp.json'.format(
            FILE_PATH.parent), ioc_file, silent=True)
        util.delete_file('{}/inputs/temp.json'.format(FILE_PATH.parent))
        print(f"New file has been created at: {ioc_file}")
    # Otherwise updating file, read JSON file to find the last index and insert the new values
    else:
        # Opening existing file
        with open(ioc_file) as file:
            lines = file.read().splitlines()
            last_index = (json.loads(lines[-2]))["index"]["_id"]
            current_index = last_index + 1
        # For every value in the list, add the attributes into the JSON
        for value in updated_values:
            list_to_push.append(
                "{\"index\":{\"_index\":\"ioc\",\"_id\":%d}}" % current_index)
            list_to_push.append(json.dumps(value))
            current_index += 1

        # Write to the JSON file
        with open(ioc_file, "a") as file:
            for line in list_to_push:
                file.write(line + "\n")

        print("BulkAPI JSON Updated!")


if __name__ == "__main__":
    main()
