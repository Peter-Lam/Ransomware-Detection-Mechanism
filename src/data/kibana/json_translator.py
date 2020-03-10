#!/usr/bin/python
'''This program provides the functions to convert a typical JSON
to the BulkAPI requirements, and vice versa '''
import json
import sys

sys.path.append('../')
import utils.file_util as util


def convert_to_bulk_api(json_path, output_path=None, silent=False):
    '''Takes regular json file and converts to bulk api json'''
    file_contents = util.load_json(json_path)
    new_contents = []
    current_index = 0
    for row in file_contents:
        new_contents.append(
            "{\"index\":{\"_index\":\"ioc\",\"_id\":%d}}" % current_index)
        current_index += 1
        new_contents.append(json.dumps(row))
    if output_path:
        util.write_bulk_api(new_contents, output_path)
        if not silent:
            print("Conversion successful, file found at {}".format(output_path))

    return new_contents


def convert_to_json(bulk_json_path, output_path=None, silent=False):
    '''Takes bulk api json and converts to regular JSON'''
    file_contents = util.load_file(bulk_json_path)
    new_contents = []
    for line in file_contents:
        if "{\"index\":" not in line:
            new_contents.append(line)
    if output_path:
        util.write_json(new_contents, output_path)
        if not silent:
            print("Conversion successful, file found at {}".format(output_path))

    return new_contents
