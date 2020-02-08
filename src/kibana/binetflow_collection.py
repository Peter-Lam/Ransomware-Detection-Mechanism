#!/usr/bin/python
'''This is a python program will collect the network flow of viruses
through requests'''

import os
import time
import urllib3
import requests

from utils.file_util import load_json, load_yaml

def main():
    '''main'''
    collect_datasets()

def collect_datasets():
    '''Retrieves dataset_json and sends request to get the bi netflow
    for each object'''
    config = load_yaml('./config.yml')
    base_url = config['stratosphere_binetflow_url']
    json_path = config['dataset_path']
    output_base_path = config['binet_output_path']
    dataset_json = get_dataset_json(json_path)
    urllib3.disable_warnings()
    for obj in dataset_json:
        download_url = 'https://' + base_url + '/' + obj['path']
        binet_flow = download_binetflow(download_url)
        path_of_virus = '/' + obj['path'].split('/')[0]
        if binet_flow:
            write_binetflow_to_file(output_base_path + path_of_virus, binet_flow)
        time.sleep(8)


def get_dataset_json(file_path):
    '''Returns the json for downloading the dataset'''
    return load_json(file_path)

def download_binetflow(url):
    '''Send an HTTP GET request to stratosphere and return contnet if status 200'''
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        print(url + ' request was successful')
        return response.content
    print(url + ' request failed')
    return None

def write_binetflow_to_file(output_path, bytes_output):
    '''Write binet flow into a file'''
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path + '.csv', 'wb') as file:
        file.write(bytes_output)

if __name__ == '__main__':
    main()
    