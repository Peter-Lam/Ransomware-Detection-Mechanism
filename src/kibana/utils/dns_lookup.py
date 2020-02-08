#!/usr/bin/python
'''Module containing functions to find ips of domains using Python Socket'''
#To input: from modules import dns_lookup
import socket
import validators

def bulk_lookup(file_path):
    '''Returns a list of resolved IPs'''
    list_ip = []
    file_path = open(file_path, "r")
    line = file_path.readline()
    while line:
        ip_addr = None
        try:
            ip_addr = get_ip_from_url(line)
        except socket.gaierror:
            print('Unable to resolve ' + line)
            line = file_path.readline()
            continue
        if ip_addr is None:
            line = file_path.readline()
            continue
        list_ip.append(ip_addr)
        line = file_path.readline()
    file_path.close()
    return list_ip

def get_ip_from_url(url):
    '''Return the ip of a given domain name'''
    try:
        domain = trim_url(url)
        validators.domain(domain)
        if validators.domain(domain):
            return socket.gethostbyname(domain)
        print('Fix format of input: ' + url)
        return None
    except socket.gaierror:
        raise socket.gaierror

def trim_url(url):
    '''trims the given url to extract the domain.'''
    www = 'www.'
    http = 'http://'
    https = 'https://'

    url = url.strip()
    if www in url:
        url = url[(url.find(www) + len(www)):]
    if http in url:
        url = url[(url.find(http) + len(http)):]
    if https in url:
        url = url[(url.find(https) + len(https)):]
    if '/' in url:
        url = url[:url.find('/')]
    domain = url.replace('[.]', '.')
    return domain
