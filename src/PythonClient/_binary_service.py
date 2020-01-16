#!/user/RDM-env/Scripts python
'''This is a python program which will be used to send requests
to VirusTotal to download ransomware binaries. Program should log
any hashes it is able to download and log ones that are not found
or failed. The download location for binaries will be based on a
yaml configuation file. API Key used must be set as an system
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
    _introduction()
    user_response = input()
    print()
    if user_response == "continue":
        config = _get_config()
        vt_url = config['vt_url']
        binaries_path = config['binaries_path']
        if vt_url != '':
            hash_json = _get_hashes()
            _download_binaries(hash_json, vt_url, binaries_path)

def _download_binaries(_hash_json, _vt_url, _file_path):
    '''Creates output path. Iterates each hash and sends request to VT to download binary.
    After it writes the contents in a file (bytes). This is the binary file which
    can be used in cuckoo.'''
    os.makedirs(_file_path, exist_ok=True)

    #HASH can also be md5/sha1/sha256 TODO
    md5_key = "md5"
    hash_list = [obj[md5_key] for obj in _hash_json]

    for md5 in hash_list:
        url = _vt_url
        params = {}
        #Read API_KEY from environment variable
        api_key = os.environ.get(API_ENV_VAR)
        if api_key:
            params[VT_API_PARAM] = api_key
            print("Attempting to download " + md5)
            params[VT_HASH_PARAM] = md5
            print(params)
            response = requests.get(url, params=params)
            print(response)
            downloaded_file = response.content
            file = open(_file_path + "\\" + md5 + ".bytes", "w+")
            file.write(downloaded_file)
            file.close()
        else:
            print("API Key Environment Variable was not set.")


def _introduction():
    '''Prints an introuction statement and warning'''
    print("This Python program is used to download binaries of viruses."
          "Please use with EXTREME CAUTION!\n"
          "Before continuing, please verify the download path"
          "and the list of hashes to be downloaded. \nDo not "
          "download and run report on the same malware twice.\n"
          "Type 'continue' to go through or 'exit' to leave program.\n")

def _get_config():
    '''Reads the configuration file and returns the object'''
    with open("config.yml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def _get_hashes():
    '''Reads a json file containing a list of hashes. THIS IS TEMPORARY; read from Elasticsearch'''
    with open('temp_hashes.json') as file:
        data = json.load(file)
        return data

if __name__ == '__main__':
    main()
