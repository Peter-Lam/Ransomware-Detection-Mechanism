#!/usr/bin/python
'''File containing validation utilities'''

import datetime
import socket


def is_valid_ipv4(value, raise_error=False):
    '''
    Check if value is a valid ipv4.
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
        # If there is an error, raise it or not depending on option
        message = (f"The following ip '{value}' is not a valid ipv4, skipping")
        if raise_error:
            raise Exception(message)
        return False


def is_valid_ipv6(value, raise_error=False, silent=False):
    '''
    Check if value is a valid ipv6.
    If raise_error is enabled then raise an error, otherwise just print a warning
    :param value: value to validate
    :param raise_error: option for error handling
    :type value: string
    :type raise_error: boolean
    :return: returns the result of validation check
    :rtype: boolean
    '''
    # Checking IPV6
    try:
        socket.inet_pton(socket.AF_INET6, value)
        return True
    except socket.error:
        # If there is an error, raise it or not depending on option
        message = (f"The following ip '{value}' is not a valid ipv6, skipping")
        if raise_error:
            raise Exception(message)
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


def is_valid_date(value, raise_error=False):
    '''
    Validating if date string is in DD/MM/YYYY format
    If raise_error is enabled then raise an error, otherwise return false
    :param value: value to validate
    :param raise_error: option for error handling
    :type value: string
    :type raise_error: boolean
    :return: returns the result of validation check
    :rtype: boolean
    '''
    try:
        date_object = datetime.datetime.strptime(value, '%m/%d/%Y')
        return True
    except ValueError as message:
        if raise_error:
            raise Exception(message)
        return False
    return False
