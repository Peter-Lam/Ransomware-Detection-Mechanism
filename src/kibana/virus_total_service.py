#!/usr/bin/python
'''This is a python program which will be used to send requests
to VirusTotal to download ransomware binaries. Program should log
any hashes it is able to download and log ones that are not found
or failed. The download location for binaries will be based on a
yaml configuration file. API Key used must be set as a system
environment variable.'''

import json
import os
import requests
import yaml

VT_API_PARAM = 'apikey'
VT_HASH_PARAM = 'hash'
API_ENV_VAR = 'RDM_API_KEY'

def main():
    '''main'''
    introduction()
    user_response = input()
    print()
    if user_response == "continue":
        config = get_config()
        vt_url = config['vt_url']
        binaries_path = config['binaries_path']
        if vt_url != '':
            hash_json = get_hashes()
            download_binaries(hash_json, vt_url, binaries_path)

def download_binaries(_hash_list, _vt_url, _file_path):
    '''Creates output path. Iterates each hash and sends request to VT to download binary.
    After it writes the contents in a file (bytes). This is the binary file which
    can be used in cuckoo.'''
    os.makedirs(_file_path, exist_ok=True)

    #HASH can also be md5/sha1/sha256 TODO
    for hash_value in _hash_list:
        url = _vt_url
        params = {}
        #Read API_KEY from environment variable
        api_key = os.environ.get(API_ENV_VAR)
        if api_key:
            params[VT_API_PARAM] = api_key
            print("Attempting to download " + hash_value)
            params[VT_HASH_PARAM] = hash_value
            print(params)
            response = requests.get(url, params=params)
            print(response)
            downloaded_file = response.content
            file = open(_file_path + "\\" + hash_value + ".bytes", "w+")
            file.write(downloaded_file)
            file.close()
        else:
            print("API Key Environment Variable was not set.")


def introduction():
    '''Prints an introduction statement and warning'''
    print("This Python program is used to download binaries of viruses."
          "Please use with EXTREME CAUTION!\n"
          "Before continuing, please verify the download path"
          "and the list of hashes to be downloaded. \nDo not "
          "download and run report on the same malware twice.\n"
          "Type 'continue' to go through or 'exit' to leave program.\n")

def get_config():
    '''Reads the configuration file and returns the object'''
    with open("config.yml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def get_hashes():
    '''Reads a JSON file containing a list of hashes. THIS IS TEMPORARY; read from Elasticsearch'''
    with open('temp_hashes.json') as file:
        data = json.load(file)
        return data

if __name__ == '__main__':
    main()
