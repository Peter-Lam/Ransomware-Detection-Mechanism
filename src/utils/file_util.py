#!/usr/bin/python
'''File containing file utility functions such as opening, reading, writing'''

import json
import yaml
import os


def load_file(path):
    '''Reads a file and returns a list of strings'''
    with open(path, 'r') as file:
        return file.read().splitlines()


def load_json(path):
    '''Opens and loads a JSON file'''
    with open(path, 'r') as file:
        return json.load(file)


def load_yaml(path):
    '''Reads the configuration file and returns the object'''
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def write_json(data, output_path):
    '''Reads values and writes into output file path, will overwrite file if already exists'''
    with open(output_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def write_bulk_api(data, output_path):
    '''Reads values and writes into output file path, will overwrite file if already exists'''
    with open(output_path, "w") as file:
        for line in data:
            file.write(line + "\n")


def update_json(data, output_path):
    '''Appends data to existing json file'''
    if os.path.exists(output_path):
        file_contents = load_json(output_path)
        for row in data:
            file_contents.append(row)
        write_json(file_contents, output_path)


def delete_file(path):
    '''Deletes file if it exists'''
    if os.path.exists(path):
        os.remove(path)
