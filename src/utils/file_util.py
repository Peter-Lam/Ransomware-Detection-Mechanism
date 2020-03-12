#!/usr/bin/python
'''File containing file utility functions such as opening, reading, writing'''

import json
import os
import yaml


def convert_to_bulk_api(json_path, output_path=None, silent=False):
    '''
    Takes regular json file and converts to bulk api json
    :param json_path: Path to regular json file to be converter
    :param output_path: Output path including filename.json
    :param silent: Option to suppress console logs
    :raises Exception: JSON path does not exist
    :type json_path: str
    :type output_path: str, optional
    :type silent: bool, optional
    :return new_contents: Returns a list of information
    :rtype: list
    '''
    if not os.path.exists(json_path):
        raise Exception(f"The path: {json_path} does not exist")

    file_contents = load_json(json_path)
    new_contents = []
    current_index = 0
    for row in file_contents:
        new_contents.append(
            "{\"index\":{\"_index\":\"ioc\",\"_id\":%d}}" % current_index)
        current_index += 1
        new_contents.append(json.dumps(row))
    if output_path:
        write_bulk_api(new_contents, output_path)
        if not silent:
            print(f"Conversion successful, file found at {output_path}")
    return new_contents


def convert_to_json(bulk_json_path, output_path=None, silent=False):
    '''
    Takes bulk api json and converts to regular JSON
    :param bulk_json_path: Path to regular json file to be converter
    :param output_path: Output path including filename.json
    :param silent: Option to suppress console logs
    :raises Exception: JSON path does not exist
    :type bulk_json_path: str
    :type output_path: str, optional
    :type silent: bool, optional
    :return new_contents: Returns a list of information
    :rtype: list
    '''
    if not os.path.exists(bulk_json_path):
        raise Exception(f"The path: {bulk_json_path} does not exist")

    file_contents = load_file(bulk_json_path)
    new_contents = []
    for line in file_contents:
        if "{\"index\":" not in line:
            new_contents.append(line)
    if output_path:
        write_json(new_contents, output_path)
        if not silent:
            print("Conversion successful, file found at {}".format(output_path))

    return new_contents


def load_file(path):
    '''
    Reads a file and returns a list of strings
    :param path: Path to file
    :type path: str
    :raises Exception: File path does not exist
    :return: File contents
    :rtype: list
    '''
    if not os.path.exists(path):
        raise Exception(f"The path: {path} does not exist")
    with open(path, 'r') as file:
        return file.read().splitlines()


def load_json(path):
    '''
    Opens and loads a JSON file
    :param path: Path to JSON
    :type path: str
    :raises Exception: JSON path does not exist
    :return: File contents
    :rtype: json
    '''
    if os.path.exists(path):
        raise Exception(f"The path: {path} does not exist")
    with open(path, 'r') as file:
        return json.load(file)


def load_yaml(path):
    '''
    Reads the configuration file and returns the object
    :param path: Path to yaml
    :type path: str
    :raises Exception: Yaml path does not exist
    :return: Config contents
    :rtype: yaml
    '''
    if not os.path.exists(path):
        raise Exception(f"The path: {path} does not exist")

    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def write_json(data, output_path):
    '''
    Reads values and writes into output file path,
    will overwrite file if already exists
    :param data: Ioc data to add write to json
    :param output_path: Output path including filename.json
    :type data: list of dict
    :type output_path: str
    '''
    with open(output_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def write_bulk_api(data, output_path):
    '''
    Writes to a json file in bulk api format given a list of information,
    if the output path already exists, will overwrite
    :param data: ioc data to add write to json
    :param output_path: the path to the json in bulk api format
    :type data: list of dict
    :type output_path: str
    '''
    new_contents = []
    current_index = 0
    for row in data:
        new_contents.append(json.dumps(
            {"index": {"_index": "ioc", "_id": current_index}}))
        current_index += 1
        new_contents.append(json.dumps(row))

    with open(output_path, "w") as file:
        for line in new_contents:
            file.write(line + "\n")


def get_last_index(bulk_api_path):
    '''
    Retreiving the last index from a JSON in bulk api format,
    will raise exception if file path doesn't exist
    :param bulk_api_path: File path to json in bulk api format
    :type bulk_api_path: str
    :raises Exception: Bulk API path does not exist
    :return last_index: The last index in the json
    :rtype last_index: int
    '''
    if not os.path.exists(bulk_api_path):
        raise Exception(f"The path: {bulk_api_path} does not exist")

    with open(bulk_api_path) as file:
        lines = file.read().splitlines()
        last_index = (json.loads(lines[-2]))["index"]["_id"]
        return last_index


def update_bulk_api(ioc_dicts, output_path):
    '''
    Updating an existing json in bulk api format with new ioc information,
    will raise exception if file path doesn't exist
    :param ioc_dicts: Ioc information that is to be added to the json
    :param output_path: The path to the json in bulk api format
    :raises Exception: Output path does not exist
    :type ioc_dicts: list of dict
    :type output_path: str
    '''
    updated_list = []
    if not os.path.exists(output_path):
        raise Exception(f"The path: {output_path} does not exist")

    # Set current index by getting last index + 1
    current_index = get_last_index(output_path) + 1
    # Add index line in-between each line of ioc data
    for value in ioc_dicts:
        updated_list.append(json.dumps(
            {"index": {"_index": "ioc", "_id": current_index}}))
        updated_list.append(json.dumps(value))
        current_index += 1

    # Write to the JSON file
    with open(output_path, "a") as file:
        for line in updated_list:
            file.write(line + "\n")


def update_json(data, output_path):
    '''
    Appends data to existing json file
    :param data: Information to be appended to json
    :param output_path: Existing JSON path
    :type data: list of dict
    :type output_path: str
    :raises Exception: JSON path does not exist
    '''
    if not os.path.exists(output_path):
        raise Exception(f"The path: {output_path} does not exist")

    file_contents = load_json(output_path)
    for row in data:
        file_contents.append(row)
    write_json(file_contents, output_path)


def delete_file(path):
    '''
    Deletes file if it exists
    :param path: Path of file
    :type: str
    '''
    if os.path.exists(path):
        os.remove(path)
