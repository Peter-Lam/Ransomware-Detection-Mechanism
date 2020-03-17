#!/usr/bin/python
'''
This service utilizes ipinfo and cymru APIs to update IP and Domains
with geolocation and asn information
'''
import pathlib
import socket
import sys
import time
import ipinfo
# https://www.team-cymru.com/IP-ASN-mapping.html
from cymruwhois import Client
sys.path.append('../../')
import utils.common as common
import utils.file_util as util

FILE_PATH = pathlib.Path(__file__).parent.absolute()
CONFIG = util.load_yaml('{}/config.yml'.format(FILE_PATH.parent.parent))


def check_ioc(ioc_type):
    '''
    Validating ioc_type for ip api collection
    :param ioc_type: The type of ioc to validate
    :type ioc_type: str
    :raises Exception: Invalid ioc type
    '''
    valid_types = ['DOMAIN', 'IP']
    if not ioc_type in valid_types:
        raise Exception(
            f"Unable to get information from ioc_type, {ioc_type}, must be {valid_types}")


def domain_to_asn(domain_list):
    '''
    Updates list of domains with asn information
    :param domain_list: A list of domains to get asn information from
    :type domain_list: list of str
    :return: Returns a dictionary with key value pairs of (domain:{asn_info})
    :rtype: dict
    '''
    ip_list, domain_ip_mapping = domain_to_ip(domain_list)
    # Removing unresolved ips
    stripped_ips = [i for i in ip_list if i] 
    ip_asn_mapping = get_asn_mapping(stripped_ips)
    # Adding empty mapping for unresolved ips
    ip_asn_mapping.update({None:{'asn': None, 'is_bell': None}})
    return merge_mappings(domain_ip_mapping, ip_asn_mapping)


def domain_to_ip(domain_list):
    '''
    Converts a list of domains and returns list of ips and a list of mappings
    :param domain_list: A list of domains to convert to ips
    :type domain_list: list of str
    :return ip_list: Returns a list of ips
    :return domain_ip_mapping: Returns a dictionary with key value pairs of (domain:ip)
    :rtype ip_list: list of str
    :rtype domain_ip_mapping: dict

    '''
    ip_list = []
    domain_ip_mapping = {}
    # Get the ips from domain name
    for domain in domain_list:
        try:
            clean_domain = common.strip_brackets(domain)
            ip_value = socket.gethostbyname(clean_domain)
        except socket.gaierror as e:
            print(f"Unable to find IP for domain {clean_domain}, skipping")
            ip_value = None
        finally:
            domain_ip_mapping.update({domain: ip_value})
            ip_list.append(ip_value)
    return ip_list, domain_ip_mapping


def get_asn_mapping(ip_list):
    '''
    Calls the cymru api service to get ASN from a given IP and checks if its from Bell
    :param ip_list: A list of ips to get asn information from
    :type ip_list: list of str
    :return mapping: Returns a dictionary with key value pairs of (ip:asn_info)
    :rtype mapping: dict
    '''
    mapping = {}
    client = Client()
    temp = 0
    try:
        # If the length of the list is 1, do a solo api call
        if len(ip_list) == 1:
            # Incase the api call returns special characters, catch error and set none
            try:
                result = client.lookup(ip_list[0])
                is_bell = result.asn in CONFIG['bell_asn'].keys()
                mapping.update(
                    {ip_list[0]: {'asn': result.asn, 'is_bell': is_bell}})
                return mapping
            except UnicodeDecodeError:
                mapping.update(
                    {ip_list[0]: {'asn': None, 'is_bell': None}})
                return mapping
        for idx, result in enumerate(client.lookupmany(ip_list)):
            is_bell = result.asn in CONFIG['bell_asn'].keys()
            mapping.update(
                {ip_list[idx]: {'asn': result.asn, 'is_bell': is_bell}})
        return mapping
    except UnicodeDecodeError:
        # Split list and recall function to find invalid api call and rejoin
        mapping_a = get_asn_mapping(ip_list[:len(ip_list)//2])
        mapping_b = get_asn_mapping(ip_list[len(ip_list)//2:])
        mapping_c = mapping_a.copy()
        mapping_c.update(mapping_b)
        return mapping_c


def get_geo_mapping(ip_list):
    '''
    Calls IPInfo api to get geoinformation from an ip list
    :param ip_list: A list of ips to get geolocation information from
    :type ip_list: list of str
    :return mapping: Returns a dictionary with key value pairs of (ip:geo_info)
    :rtype mapping: dict
    '''
    while True:
        try:
            mapping = {}
            # Calling ipinfo with given api key, returning handler
            api_key = CONFIG['ip_api']
            handler = ipinfo.getHandler(access_token=api_key)
            for idx, val in enumerate(ip_list):
                # Getting all details and updating each dict in the list
                details = handler.getDetails(val).all
                # Checking keys in returned data and setting variables accordingly
                # If the key doesn't exists then just set value to None
                keys = details.keys()
                org = details['org'] if 'org' in keys and details['org'] else None
                city = details['city'] if 'city' in keys and details['city'] else None
                latitude = float(
                    details['latitude']) if 'latitude' in keys and details['latitude'] else None
                longitude = float(
                    details['longitude']) if 'longitude' in keys and details['longitude'] else None
                postal = details['postal'] if 'postal' in keys and details['postal'] else None
                region = details['region'] if 'region' in keys and details['region'] else None
                mapping.update({ip_list[idx]: {'city': city, 'latitude': latitude,
                                                'longitude': longitude, 'postal': postal,
                                                'region': region, 'org': org}})
            return mapping
        except requests.exceptions.ReadTimeout: 
            print("Connection Timeout, waiting to reconnect")
            time.sleep(60)

def merge_mappings(main_dict, second_dict):
    '''
    Merge two dictionaries on value of main_dict and key of second_dict
    :param main_dict: First dictionary (A:B)
    :param second_dict: Second dictionary (B:C)
    :type main_dict: dict
    :type second_dict: dict
    :return result_mapping: Merges mapping (A:C)
    :rtype result_mapping: dict
    '''
    result_mapping = {}
    for key, val in main_dict.items():
        value_dict = second_dict.get(val)
        value_dict.update({'ip':val})
        result_mapping.update({key: value_dict})
    return result_mapping


def update_dict(list_of_dicts, mapping):
    '''
    Update existing dictionary with new values from mappings
    :param list_of_dicts: The list of IOC dictionaries that will be updated
    :param mapping: The dictionaries that contain key value pairs of (IOC_value, new_values)
    :type list_of_dicts: list of dict
    :type mapping: dict
    :return: Returns the updated dictionary of IOCs
    :rtype: list of dict
    '''
    for value in list_of_dicts:
        # Get a dictionary of values (i.e. {asn:__, is_bell:__})
        to_update = mapping.get(value['value'])
        value.update(to_update)
    return list_of_dicts


def update_all(list_of_dicts, ioc_type):
    '''
    Updates ASN and Geo information using APis
    :param list_of_dicts: The list of IOC dictionaries that will be updated
    :param ioc_type: The type of ioc (i.e. url, domain, ip)
    :type list_of_dicts: list of dict
    :type ioc_type: str
    :return: Returns the updated dictionary of IOCs
    :rtype: list of dict
    '''
    geo_dict = update_geo_info(list_of_dicts, ioc_type)
    asn_geo_dict = update_asn_info(geo_dict, ioc_type)
    return asn_geo_dict


def update_asn_info(list_of_dicts, ioc_type):
    '''
    Calls the cymru api service to get ASN from a given IP and checks if its from Bell
    :param list_of_dicts: The list of IOC dictionaries that will be updated
    :param ioc_type: The type of ioc (i.e. url, domain, ip)
    :type list_of_dicts: list of dict
    :type ioc_type: str
    :return: Returns the updated dictionary of IOCs
    :rtype: list of dict
    '''
    value_list = []
    # Validating ioc_type
    check_ioc(ioc_type)
    # Get the values for the ioc_type
    for ioc in list_of_dicts:
        value_list.append(ioc['value'])
    if ioc_type == 'DOMAIN':
        asn_mapping = domain_to_asn(value_list)
    # If not domain then its ip, so call the ip_to_asn function
    else:
        asn_mapping = get_asn_mapping(value_list)
    # Return the updated list_of_dicts with the ASN values
    return update_dict(list_of_dicts, asn_mapping)


def update_geo_info(list_of_dicts, ioc_type):
    '''
    Given api key and a list of ip dictionaries, updates with geolocation info
    :param list_of_dicts: The list of IOC dictionaries that will be updated
    :param ioc_type: The type of ioc (i.e. url, domain, ip)
    :type list_of_dicts: list of dict
    :type ioc_type: str
    :return: Returns the updated dictionary of IOCs
    :rtype: list of dict
    '''
    value_list = []
    # Validating ioc_type
    check_ioc(ioc_type)
    # Get the values for the ioc_type
    for ioc in list_of_dicts:
        value_list.append(ioc['value'])
    if ioc_type == 'DOMAIN':
        ip_list, domain_ip_mapping = domain_to_ip(value_list)
        ip_geo_mapping = get_geo_mapping(ip_list)
        geo_mapping = merge_mappings(domain_ip_mapping, ip_geo_mapping)
    # If not domain then its ip, so call the ip_to_asn function
    else:
        geo_mapping = get_geo_mapping(value_list)
    # Return the updated list_of_dicts with the ASN values
    return update_dict(list_of_dicts, geo_mapping)
