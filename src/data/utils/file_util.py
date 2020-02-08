#!/usr/bin/python
'''File containing file utility functions such as opening, reading, writing'''

import json
import yaml

def load_json(path):
    '''Opens a loads a python file'''
    with open(path, 'r') as file:
        return json.load(file)

def load_yaml(path):
    '''Reads the configuration file and returns the object'''
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)
