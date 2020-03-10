#!/usr/bin/python
'''Updating an IP list with information from ipinfo api'''

import ipinfo
import pprint
import pathlib
import sys
sys.path.append('../')
import utils.file_util as util

FILE_PATH = pathlib.Path(__file__).parent.absolute()
CONFIG = util.load_yaml('{}/config.yml'.format(FILE_PATH.parent))


def ip_info_service(api_key, list_of_ip_dicts):
    '''Given api key and a list of ip dictionaries, updates info'''
    # Calling ipinfo with given api key, returning handler
    handler = ipinfo.getHandler(access_token=api_key)
    for ip in list_of_ip_dicts:
        ip_value = ip['value']
        # getting all details and updating each dict in the list
        details = (handler.getDetails(ip_value)).all
        keys = details.keys()
        city = details['city'] if 'city' in keys and details['city'] else None
        latitude = details['latitude'] if 'latitude' in keys and details['latitude'] else None
        longitude = details['longitude'] if 'longitude' in keys and details['longitude'] else None
        postal = details['postal'] if 'postal' in keys and details['postal'] else None
        region = details['region'] if 'region' in keys and details['region'] else None
        if 'org' in keys and details['org']:
            org = details['org']
            isBell = True if 'bell' in details['org'].lower() else False
        else:
            org = None
            isBell = None
        ip.update({'city': city, 'latitude': latitude,
                   'longitude': longitude, 'org': org, 'postal': postal,
                   'region': region, 'isBell': isBell})
    return list_of_ip_dicts
