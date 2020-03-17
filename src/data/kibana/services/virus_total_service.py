#!/usr/bin/python
'''This python script updates the existing ioc dictionary to add more values for Kibana.'''

import time
import pathlib
import json
import sys
import requests
from datetime import datetime
sys.path.append('../../')
import utils.file_util as util
FILE_PATH = pathlib.Path(__file__).parent.absolute()
CONFIG = util.load_yaml('{}/config.yml'.format(FILE_PATH.parent.parent))

def call_api(vt_url, resource_name, resource):
    '''
    Calling the VirusTotal API and returns JSON
    :param vt_url: The url used for api call
    :param resource_name: Name of resource used by VT API
    :param resource: The resource itself (i.e. domain, ip, url)
    :type vt_url: str
    :type resource_name: str
    :type resource: str
    :return: JSON response from VT API
    :rtype: json
    '''
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
    '''
    Updates ioc hash dictionaries with VT data
    :param hash_list: The list of hashes that need to be updated
    :param vt_url: URL used for VT API call
    :param api_limit: The API call limit of the API key, if public usually 4
    :param debug: Debug mode option to add extra console logs
    :type hash_list: list of dict
    :type vt_url: str
    :type api_limit: int
    :type debug: bool, optional
    :return hast_list: Returns updated hash information
    :rtype hash_list: list of dict
    '''
    print("Gathering hash information from Virus Total...")
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
            for index, value in enumerate(response):
                total = value["total"] if "total" in value else None
                positives = value["positives"] if "positives" in value else None
                scan_date = value["scan_date"] if "scan_date" in value else None
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
    '''
    Updates ioc ip dictionaries with VT data
    :param ip_list: The list of ips that need to be updated
    :param vt_url: URL used for VT API call
    :param api_limit: The API call limit of the API key, if public usually 4
    :param debug: Debug mode option to add extra console logs
    :type ip_list: list of dict
    :type vt_url: str
    :type api_limit: int
    :type debug: bool, optional
    :return hast_list: Returns updated ip information
    :rtype hash_list: list of dict'''
    print("Gathering ip information from Virus Total...")
    # Loop through list and call API, can't chain values like populate_hash
    for value in ip_list:
        resource = value['value']
        # Call VT Api
        response = call_api(vt_url, "ip", resource)
        # Update existing hashes
        country = response["country"] if "country" in response else None
        continent = response["continent"] if "continent" in response else None
        if "detected_urls" in response and len(response["detected_urls"]) != 0:
            total_detected_urls = len(response["detected_urls"])
            total = 0
            positives = 0
            latest_scan_date = ''
            first_scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Going through all urls associated with the domain
            for row in response["detected_urls"]:
                total += row["total"]
                positives += row["positives"]
                scan_date = row["scan_date"]
                if scan_date > latest_scan_date:
                    latest_scan_date = scan_date
                if scan_date < first_scan_date:
                    first_scan_date = scan_date
            percent = round((positives/total)*100, 2)
        else:
            total = None
            positives = None
            percent = None
            latest_scan_date = None
            first_scan_date = None
            total_detected_urls = 0

        # Updating dictionaries with new values
        value.update({'is_valid': response["response_code"], 'country': country,
                      'continent': continent,
                      'total_detected_urls': total_detected_urls, 'total': total,
                      'positives': positives, 'percent_score': percent,
                      'lastest_scan_date': latest_scan_date, 'first_scan_date': first_scan_date})

        # Writing to JSON at every iteration incase it breaks
        if debug:
            util.write_json(
                ip_list, "{}/inputs/ip_logs.json".format(FILE_PATH.parent))

    return ip_list


def populate_domain(domain_list, vt_url, debug=None):
    '''
    Updates ioc populate_domain dictionaries with VT data
    :param populate_domain: The list of domains that need to be updated
    :param vt_url: URL used for VT API call
    :param api_limit: The API call limit of the API key, if public usually 4
    :param debug: Debug mode option to add extra console logs
    :type populate_domain: list of dict
    :type vt_url: str
    :type api_limit: int
    :type debug: bool, optional
    :return hast_list: Returns updated domain information
    :rtype hash_list: list of dict'''
    # Loop through list and call API, can't chain values like populate_hash
    print("Gathering domain information from Virus Total...")
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
            first_scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Going through all urls associated with the domain
            for row in response["detected_urls"]:
                total += row["total"]
                positives += row["positives"]
                scan_date = row["scan_date"]
                if scan_date > latest_scan_date:
                    latest_scan_date = scan_date
                if scan_date < first_scan_date:
                    first_scan_date = scan_date
            percent = round((positives/total)*100, 2) if total != 0 else 0

            # Updating dictionaries with new values
            domain.update({'is_valid': is_valid, 'total_detected_urls': total_detected_urls,
                           'total': total, 'positives': positives, 'percent_score': percent,
                           'latest_scan_date': latest_scan_date, 'first_scan_date': first_scan_date})
        else:
            domain.update({'is_valid': is_valid, 'total': None,
                           'positives': None, 'percent_score': None, 'latest_scan_date': None, 'first_scan_date': None})

        # Writing to JSON at every iteration incase it breaks
        if debug:
            util.write_json(
                domain_list, "{}/inputs/domain_logs.json".format(FILE_PATH.parent))

    return domain_list