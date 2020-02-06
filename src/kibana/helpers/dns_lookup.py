#!/usr/bin/python
'''Module containing functions to find ips of domains using Python Socket'''
#To input: from modules import dns_lookup
import socket
import validators

def bulk_lookup(file_path):
    '''Returns a list of resolved IPs'''
    list_ip = []
    fp = open(file_path, "r")
    line = fp.readline()
    while line:
        try:
            ip = get_ip_from_url(line)
        except (socket.gaierror):
            print('Unable to resolve ' + line)
            line = fp.readline()
            continue
        if (ip == None):
            line = fp.readline()
            continue
        list_ip.append(ip)
        line = fp.readline()
    fp.close()
    return list_ip

def get_ip_from_url(url):
    '''Return the ip of a given domain name'''
    try:
        domain = trim_url(url)
        validators.domain(domain)
        if (validators.domain(domain)):
            return socket.gethostbyname(domain)
        else:
            print('Fix format of input: ' + url)
    except (socket.gaierror):
        raise (socket.gaierror)
    except:
        return None

def trim_url(url):
    '''trims the given url to extract the domain.'''
    WWW = 'www.'
    HTTP = 'http://'
    HTTPS = 'https://'

    url = url.strip()
    if (WWW in url):
        url = url[(url.find(WWW) + len(WWW)):]
    if (HTTP in url):
        url = url[(url.find(HTTP) + len(HTTP)):]
    if (HTTPS in url):
        url = url[(url.find(HTTPS) + len(HTTPS)):]
    if ('/' in url):
        url = url[:url.find('/')]
    domain = url.replace('[.]', '.')
    return domain