#!/usr/bin/python
'''This python script will update the existing ioc list to add more values for Kibana.'''

import time
import pathlib
import json
import sys
import requests
sys.path.append('../')
import json_translator as translator
import utils.file_util as util
VT_API_PARAM = 'apikey'
VT_HASH_PARAM = 'hash'
API_ENV_VAR = 'RDM_API_KEY'
FILE_PATH = pathlib.Path(__file__).parent.absolute()
CONFIG = util.load_yaml('{}/config.yml'.format(FILE_PATH.parent))


def get_values(bulk_api_file_path):
    '''Gather the values of returning lists of hashes, ips and urls'''
    ioc_list = translator.convert_to_json(bulk_api_file_path)
    hash_list = []
    ip_list = []
    domain_list = []
    for ioc in ioc_list:
        if (json.loads(ioc))["type"] == "MD5" or (json.loads(ioc))["type"] == "SHA256":
            hash_list.append((json.loads(ioc)))
        if (json.loads(ioc))["type"] == "IP":
            ip_list.append((json.loads(ioc)))
        if (json.loads(ioc))["type"] == "DOMAIN":
            domain_list.append((json.loads(ioc)))
    return hash_list, ip_list, domain_list


def call_api(vt_url, resource_name, resource):
    '''Calling the VirusTotal API and returns JSON'''
    counter = 0
    params = {'apikey': CONFIG['api_key'][0]}
    num_of_keys = len(CONFIG['api_key'])
    # Calling VT API
    params.update({f'{resource_name}': resource})
    response = requests.get(vt_url, params=params)
    # If error received, likely due to exceeding api limit calls per minute, if so just wait 60secs
    while not response.status_code == 200:
        if response.status_code != 204:
            print(
                f"{response.status_code} = You have been blocked using API key #{counter}")
        # Checking other API keys
        if counter < num_of_keys-1:
            counter += 1
            # print(f"{response.status_code} - HTTP Request Error, trying API key #{counter+1}")
            params.update({'apikey': CONFIG['api_key'][counter]})
            response = requests.get(vt_url, params=params)
        # Reset counter and just wait for the API
        else:
            counter = 0
            # print("{} - HTTP Request Error, waiting 60secs for API key to refresh"
            # .format(response.status_code))
            time.sleep(60)
            # print("Remaking API call...")
            params.update({'apikey': CONFIG['api_key'][counter]})
            response = requests.get(vt_url, params=params)
    return response.json()


def populate_hash(hash_list, vt_url, api_limit, debug=None):
    '''Populating rows with hashes with missing data, returns lists of dicts of updated data'''

    hash_len = len(hash_list)
    # Loop through list, incrementing by api call limit each time
    for num in range(0, hash_len, api_limit):
        resource = ''
        chain_count = 0
        # Creating a sub-loop that to add values needed for API call
        for index in range(num, num+api_limit):
            # Don't add resource if out of index
            if index >= hash_len:
                break
            resource += (hash_list[index]['value'])
            if index != (num+api_limit-1):
                resource += ", "
            chain_count += 1
        # Call VT Api
        response = call_api(vt_url, "resource", resource)

        if chain_count == 1:
            total = response["total"] if "total" in response else None
            positives = response["positives"] if "positives" in response else None
            scan_date = response["scan_date"] if "scan_date" in response else None
            percent = round((positives/total)*100,
                            2) if (positives and total) else None

            # Updating dictionaries with new values
            hash_list[num].update(
                {'total': total, 'positives': positives,
                 'percent_score': percent, 'scan_date': scan_date})
        else:
            # Update existing hashes
            for index in range(len(response)):
                total = response[index]["total"] if "total" in response[index] else None
                positives = response[index]["positives"] if "positives" in response[index] else None
                scan_date = response[index]["scan_date"] if "scan_date" in response[index] else None
                percent = round((positives/total)*100,
                                2) if (positives and total) else None

                # Updating dictionaries with new values
                hash_list[num+index].update({'total': total, 'positives': positives,
                                             'percent_score': percent, 'scan_date': scan_date})

        # Writing to JSON at every iteration incase it breaks
        if debug:
            util.write_json(
                hash_list, "{}/inputs/logs.json".format(FILE_PATH.parent))

    return hash_list


def populate_ip(ip_list, vt_url, debug=None):
    '''Populating ip_list of extra information'''
    # Loop through list and call API, can't chain values like populate_hash
    for value in ip_list:
        resource = value['value']
        # Call VT Api
        response = call_api(vt_url, "ip", resource)
        is_valid = response["response_code"]
        # Update existing hashes
        country = response["country"] if "country" in response else None
        continent = response["continent"] if "continent" in response else None
        if "detected_urls" in response and len(response["detected_urls"]) != 0:
            total_detected_urls = len(response["detected_urls"])
            total = 0
            positives = 0
            latest_scan_date = ''
            # Going through all urls associated with the domain
            for row in response["detected_urls"]:
                total += row["total"]
                positives += row["positives"]
                scan_date = row["scan_date"]
                if scan_date > latest_scan_date:
                    latest_scan_date = scan_date
            percent = round((positives/total)*100, 2)
        else:
            total = None
            positives = None
            percent = None
            latest_scan_date = None
            total_detected_urls = 0

        # Updating dictionaries with new values
        value.update({'is_valid': is_valid, 'country': country, 'continent': continent,
                      'total_detected_urls': total_detected_urls, 'total': total,
                      'positives': positives, 'percent_score': percent,
                      'scan_date': scan_date})

        # Writing to JSON at every iteration incase it breaks
        if debug:
            util.write_json(
                ip_list, "{}/inputs/ip_logs.json".format(FILE_PATH.parent))

    return ip_list


def populate_domain(domain_list, vt_url, debug=None):
    '''Populating domain_list of extra information'''
    # Loop through list and call API, can't chain values like populate_hash
    for domain in domain_list:
        resource = (domain['value']).replace('[', '').replace(']', '').strip()
        # Call VT Api
        response = call_api(vt_url, "domain", resource)
        # Update existing hashes
        is_valid = response["response_code"]
        if is_valid:
            total_detected_urls = len(response["detected_urls"])
            total = 0
            positives = 0
            latest_scan_date = ''
            # Going through all urls associated with the domain
            for row in response["detected_urls"]:
                total += row["total"]
                positives += row["positives"]
                scan_date = row["scan_date"]
                if scan_date > latest_scan_date:
                    latest_scan_date = scan_date
            percent = round((positives/total)*100, 2)

            # Updating dictionaries with new values
            domain.update({'is_valid': is_valid, 'total_detected_urls': total_detected_urls,
                           'total': total, 'positives': positives, 'percent_score': percent,
                           'scan_date': latest_scan_date})
        else:
            domain.update({'is_valid': is_valid, 'total': None,
                           'positives': None, 'percent_score': None, 'scan_date': None})

        # Writing to JSON at every iteration incase it breaks
        if debug:
            util.write_json(
                domain_list, "{}/inputs/domain_logs.json".format(FILE_PATH.parent))

    return domain_list


def populate_all(ioc_path=None):
    '''Populating hash ip and domain list with VT info'''
    file_path = ioc_path if ioc_path else '{}/inputs/ioc_list.json'.format(
        FILE_PATH.parent)

    hash_list, ip_list, domain_list = get_values(file_path)
    print("Populating domain information")
    updated_domain = populate_domain(
        domain_list, CONFIG['vt_domain'])
    print("Populating ip information")
    updated_ip = populate_ip(ip_list, CONFIG['vt_ip'])
    print("Populating hash information (this may take a while)")
    updated_hash = populate_hash(
        hash_list, CONFIG['vt_report'], CONFIG['api_limit'])
    new_json = []
    for row in updated_domain:
        new_json.append(row)
    for row in updated_ip:
        new_json.append(row)
    for row in updated_hash:
        new_json.append(row)
    return new_json


def main():
    '''main'''
    new_json = populate_all()
    util.write_json(new_json, '{}/inputs/temp2.json'.format(FILE_PATH.parent))
    translator.convert_to_bulk_api('{}/inputs/temp2.json'.format(
        FILE_PATH.parent), '{}/inputs/ioc_list_final.json'.format(FILE_PATH.parent))
    util.delete_file('{}/inputs/temp2.json'.format(FILE_PATH.parent))


if __name__ == '__main__':
    main()
