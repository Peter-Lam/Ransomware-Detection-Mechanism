#!/usr/bin/python
'''File containing common used functions'''

def strip_brackets(value):
    '''
    Stripping a string of [] and extra spaces
    :param value: value to manipulate
    :return: stripped version of value
    :rtype: string
    '''
    return value.replace('[', '').replace(']', '').strip()
