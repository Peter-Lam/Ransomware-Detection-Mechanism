#!/usr/bin/python
'''
    This is a python program which is used to automate the process of
    updating ioc JSON file with the appropriate values
'''

import sys
import os.path as path
import json


def check_arguments(list_of_args):
    '''Checks the arguments for proper inputs'''
    # Checking for 5 arguments
    if len(list_of_args) != 5:
        sys.exit("Error: Must provide the following pattern: pushToJSON.py [Path to ioc_list.json]"
                 "[URL to Source] [malware type] [IOC type] [PATH to value text file]\n"
                 "EXAMPLE: python update_json.py src\\ioc_list_copy.json"\
                 "virusshare.com emotet MD5 \"7da0435335afc\"")
    if not path.exists(list_of_args[0]):
        sys.exit("The following path '{}' does not exist".format(
            list_of_args[0]))
    if not path.exists(list_of_args[4]):
        sys.exit("The following path '{}' does not exist".format(
            list_of_args[4]))

def main(argv):
    '''main'''
    check_arguments(argv)
    # Declaring variables
    ioc_file = argv[0]
    source = argv[1]
    malware_type = argv[2]
    ioc_type = argv[3]
    values_file = argv[4]
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
    main(sys.argv[1:])
