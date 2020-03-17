#!/usr/bin/python
'''This is a python program which is used to automate the process of
appending or creating a new ioc JSON file with the appropriate values'''
import argparse
import os.path as path
import pathlib
import sys
from distutils.util import strtobool
from urllib.parse import urlparse
sys.path.append('../')
import utils.validator as validator
import utils.file_util as util
import utils.common as common
import kibana.services.virus_total_service as vt_updater
import kibana.services.ip_info_service as ip_updater

# Declaring globals
FILE_PATH = pathlib.Path(__file__).parent.absolute()
# Holds VT API information
CONFIG = util.load_yaml('{}/config.yml'.format(FILE_PATH.parent))


def argparser():
    '''Parses the user arguments and checks path correct paths'''
    parser = argparse.ArgumentParser(
        description="Appending or creating new json files with new information")
    # Making new file and update file mutually exclusive options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-new', '--new', dest='new_path', metavar='',
                       help='writes to the full path of desired json file\
                            (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json',
                       action='store')
    group.add_argument('-update', '--update', dest='existing_path', metavar='',
                       help='appends the existing BULK api json file with new data\
                            (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json',
                       action='store')
    parser.add_argument('-text', '--text', dest='values_path', metavar='',
                        required=True, help='text file containing values of the iocs',
                        action='store')
    parser.add_argument('-malware', '--malware', dest='malware', metavar='',
                        required=True, help='type of malware (e.g. Trickbot)', action='store')
    parser.add_argument('-ioc', '--ioc_type', type=str.upper, dest='ioc', nargs=1,
                        choices=['MD5', 'SHA256', 'IP',
                                 'URL', 'DOMAIN', 'other'],
                        metavar='', required=True,
                        help='type of ioc (MD5|SHA256|IP|URL|DOMAIN|other)',
                        action='store')
    parser.add_argument('-src', '--source', dest='source', metavar='', required=True,
                        help='Source of malware dataset(e.g. www.virusshare.com)',
                        action='store')
    args = parser.parse_args()
    # Checking validity pf paths
    if args.existing_path and not path.exists(args.existing_path):
        parser.error(f"The file {args.existing_path} does not exist!")
    if args.new_path and path.exists(args.new_path):
        answer = input(
            "The destination path already exists at: \
             %s\nWould you like to overwrite (Y/N)? " % args.new_path)
        try:
            if strtobool(answer):
                print("Overwriting existing file")
            else:
                parser.error("Please choose another path")
        except ValueError:
            parser.error("Invalid answer, please select 'Y' or 'N' next time")

    if not path.exists(args.values_path):
        parser.error(f"The file {args.values_path} does not exist!")
    return args


def parse_url_dict(url_list, url_type):
    '''
    Breaking URL for query, path, filename, domain
    :param url_list: list of urls to parse
    :param url_type: the type of url being passed could be the value or source
    :type url_list: list of dict
    :type url_type: str
    :return: returns an updated dictionary with parsed url as new values
    :rtype: list of dict
    '''
    for url_dict in url_list:
        if url_dict[url_type]:
            url = url_dict[url_type].replace('[', '').replace(']', '').strip()
            if "://" not in url:
                url = f"http://{url}"
                parsed = urlparse(url)
                url_scheme = None
            else:
                parsed = urlparse(url)
                url_scheme = parsed.scheme
            url_query = parsed.query
            url_path = parsed.path
            url_domain = parsed.netloc
            url_hostname = parsed.hostname
            url_filename = pathlib.Path(url).stem
            url_file_ext = pathlib.Path(url).suffix
            if url_file_ext in url_filename or url_file_ext in url_domain:
                url_file_ext = ""
            if url_file_ext == "":
                url_filename = ""

            url_dict.update({url_type+'_url_query': url_query,
                             url_type + '_url_path': url_path,
                             url_type + '_url_filename': url_filename,
                             url_type + '_url_file_ext': url_file_ext,
                             url_type + '_url_scheme': url_scheme,
                             url_type + '_url_hostname': url_hostname,
                             url_type + '_url_domain': url_domain})
        else:
            url_dict.update({url_type+'_url_query': None,
                    url_type + '_url_path': None,
                    url_type + '_url_filename': None,
                    url_type + '_url_file_ext': None,
                    url_type + '_url_scheme': None,
                    url_type + '_url_hostname': None,
                    url_type + '_url_domain': None})
    return url_list


def call_apis(list_values, ioc_type):
    '''
    Calling VT, IPInfo, Cymru APIS to updating values to ioc dict
    :param list_values: the list of ioc dictionaries to update
    :param ioc_type: the type of ioc (i.e. domain, md5, sha256, ip, url)
    :type list_values: list of dict
    :type ioc_type: str
    :return updated_values: returns updated api information
    :rtype: list of dict
    '''
    if len(list_values) == 0:
        # print(f"No valid values found for ioc type: '{ioc_type}', not calling api")
        updated_values = None
    elif ioc_type in ('MD5', 'SHA256'):
        updated_values = vt_updater.populate_hash(
            list_values, CONFIG['vt_report'], CONFIG['api_limit'])
    elif ioc_type == 'IP':
        vt_updated_values = vt_updater.populate_ip(
            list_values, CONFIG['vt_ip'])
        print("Gathering ip information from IPInfo and Cymru")
        updated_values = []
        for num in range(0, len(list_values), 100):
            updated_values += ip_updater.update_all(vt_updated_values[num:num+100], ioc_type)
    elif ioc_type in ('URL', 'DOMAIN'):
        vt_updated_values = vt_updater.populate_domain(
            list_values, CONFIG['vt_domain'])
        print(f"Gathering {ioc_type} information from IPInfo and Cymru")
        ip_updated_values = ip_updater.update_all(vt_updated_values, ioc_type)
        updated_values = parse_url_dict(ip_updated_values, 'value')
    else:
        updated_values = list_values
    return updated_values


def set_basic_info(list_values, ioc_type, malware, source):
    '''
    Setting basic ioc information based on cmd arguments
    returning a list of dictionaries containing type, value, malware, and source
    :param list_values: list of values
    :param ioc_type: type of ioc (i.e. md5, sha256, ip, domain, url)
    :param malware: type of malware (i.e. emotet, ryuk, trickbot)
    :param source: source url where iocs were posted (i.e. pastebin, twitter)
    :type list_values: list
    :type ioc_type: string
    :type malware: string
    :type source: string
    :return baseinfo: returns a list of dictionaries containing type, value, malware, and source
    :rtype: list of dict
    '''
    base_info = []
    # Loop through and add basic ioc information from args
    for value in list_values:
        # Only remove [] from IP but not others, like urls and domain to prevent accidental clicks
        if ioc_type == 'IP':
            resource = common.strip_brackets(value)
            # If the ip is not valid, print warning and skip this value
            if not validator.is_valid_ip(resource):
                continue
        else:
            # If the ioc type is a hash but not a validone, print a warning and skip it
            resource = value.strip()
            if ioc_type == 'MD5' and not validator.is_valid_md5(resource):
                continue
            if ioc_type == 'SHA256' and not validator.is_valid_sha256(resource):
                continue
        base_info.append({'type': ioc_type, 'value': resource,
                          'malware': malware, 'source': source})
    return parse_url_dict(base_info, 'source')


def main():
    '''main'''
    args = argparser()

    # Read text file and grabbing a list of values
    list_values = util.load_file(args.values_path)

    # Set the basic info given by args
    base_info = set_basic_info(
        list_values, args.ioc[0], args.malware.lower(), args.source)

    # Populate missing data with various apis
    updated_values = call_apis(base_info, args.ioc[0])

    # If updating file, read JSON file to find the last index and insert the new values
    if args.existing_path:
        print("Updating existing JSON...")
        ioc_file = args.existing_path
        util.update_bulk_api(updated_values, ioc_file)

        print(f"BulkAPI JSON Updated at: {ioc_file}")
    # If its a new file, then create and write to a new file
    else:
        print("Writing to new JSON...")
        ioc_file = args.new_path
        util.write_bulk_api(updated_values, ioc_file)
        print(f"New file has been created at: {ioc_file}")


if __name__ == "__main__":
    main()
