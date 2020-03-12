#!/usr/bin/python
'''File containing validation utilities'''

import socket


def is_valid_ip(value, raise_error=False):
    '''
    Check if value is a valid ipv4 or ipv6.
    If raise_error is enabled then raise an error, otherwise just print a warning
    :param value: value to validate
    :param raise_error: option for error handling
    :type value: string
    :type raise_error: boolean
    :return: returns the result of validation check
    :rtype: boolean
    '''
    # Checking IPV4
    try:
        socket.inet_aton(value)
        return True
    except socket.error:
        pass
    # Checking IPV6
    try:
        socket.inet_pton(socket.AF_INET6, value)
        return True
    except socket.error:
        pass
    # If there is an error, raise it or print depending on option
    message = (f"The following ip is not a valid ipv4 or ipv6, {value}")
    if raise_error:
        raise Exception(message)
    print(message)
    return False


def is_valid_md5(value, raise_error=False):
    '''
    Validating if hash is an MD5
    If raise_error is enabled then raise an error, otherwise just print a warning
    :param value: value to validate
    :param raise_error: option for error handling
    :type value: string
    :type raise_error: boolean
    :return: returns the result of validation check
    :rtype: boolean
    '''
    if len(value) == 32:
        return True
    # If there is an error, raise it or print depending on option
    message = (f"The following MD5 is not the proper format: {value},\
                 did you mean another hash type? ")
    if raise_error:
        raise Exception(message)
    print(message)
    return False


def is_valid_sha256(value, raise_error=False):
    '''
    Validating if hash is an SHA256
    If raise_error is enabled then raise an error, otherwise just print a warning
    :param value: value to validate
    :param raise_error: option for error handling
    :type value: string
    :type raise_error: boolean
    :return: returns the result of validation check
    :rtype: boolean
    '''
    if len(value) == 64:
        return True
    message = (f"The following SHA256 is not the proper format: {value},\
                 did you mean another hash type? ")
    if raise_error:
        raise Exception(message)
    print(message)
    return False
