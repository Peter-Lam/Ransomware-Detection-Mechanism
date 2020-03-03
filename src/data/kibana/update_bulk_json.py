#!/usr/bin/python
'''This is a python program which is used to automate the process of
updating ioc JSON file with the appropriate values'''

import argparse
import os.path as path
import json


def argparser():
    '''Parses the user arguments and checks path correct paths'''
    parser = argparse.ArgumentParser(
        description="update_json - Updating existing json files with more datasets")
    parser.add_argument('-j', '--json', dest='json_path', metavar='', required=True,
                        help='full path of json file (BulkAPI or regular json)', action='store')
    parser.add_argument('-v', '--value', dest='values_path', metavar='',
                        required=True, help='file containing values of the iocs', action='store')
    parser.add_argument('-m', '--malware_type', dest='malware', metavar='',
                        required=True, help='type of malware (e.g. Trickbot)', action='store')
    parser.add_argument('-ioc', '--ioc_type', type=str.upper, dest='ioc', nargs=1,
                        choices=['MD5', 'SHA256', 'IP',
                                 'URL', 'DOMAIN', 'other'],
                        metavar='', required=True,
                        help='type of ioc (MD5|SHA256|IP|URL|DOMAIN|other)',
                        action='store')
    parser.add_argument('-url', '--url', dest='url', metavar='', required=True,
                        help='URL source of the malware (e.g. www.virusshare.com)', action='store')
    args = parser.parse_args()
    if not path.exists(args.json_path):
        parser.error("The file %s does not exist!" % args.json_path)
    if not path.exists(args.values_path):
        parser.error("The file %s does not exist!" % args.values_path)
    return args


def main():
    '''main'''
    args = argparser()
    # Declaring variables
    ioc_file = args.json_path
    source = args.url
    malware_type = args.malware
    ioc_type = (args.ioc)[0]
    values_file = args.values_path
    list_to_push = []
    list_values = []
    current_index = None

    # Read JSON file to find the last index
    with open(ioc_file) as file:
        lines = file.read().splitlines()
        last_index = (json.loads(lines[-2]))["index"]["_id"]
        current_index = last_index + 1

    # Read file and grabbing a list of values
    with open(values_file) as file:
        list_values = file.read().splitlines()

    # For every value in the list, add the attributes into the JSON
    for value in list_values:
        list_to_push.append(
            "{\"index\":{\"_index\":\"ioc\",\"_id\":%d}}" % current_index)
        list_to_push.append("{\"type\":\"" + ioc_type + "\",\"value\":\"" + value.strip() +
                            "\",\"malware\":\"" + malware_type + "\",\"source\":\"" +
                            source + "\"}")
        current_index += 1

    # Write to the JSON file
    with open(ioc_file, "a") as file:
        for line in list_to_push:
            file.write(line + "\n")

    print("JSON Updated!")


if __name__ == "__main__":
    main()
