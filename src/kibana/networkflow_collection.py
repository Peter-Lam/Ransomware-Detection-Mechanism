#!/usr/bin/python
'''This is a python program will collect the network flow of viruses
through scrapping and requsting'''

import json
import os
import requests
import yaml

def main():
    '''main'''
    config = get_config()
    elastic_search = config['elastic_search_url']
    stratosphere_ds_url = config['stratosphere_ds_url']
    stratosphere_binetflow_url = config['stratosphere_binetflow_url']
    response = requests.get('mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-259-1/2017-05-15_win8.binetflow', verify=False)
    downloaded_file = response.content
    file = open('test' + ".txt", "wb")
    file.write(downloaded_file)
    file.close()

def get_config():
    '''Reads the configuration file and returns the object'''
    with open("config.yml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == '__main__':
    main()
