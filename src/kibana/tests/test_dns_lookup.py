#!/usr/bin/python
'''Test file to test dns_lookup'''
import socket
import sys
import unittest
import validators

sys.path.append('../')
from helpers import dns_lookup # pylint: disable=E0611,C0413

class TestDNSLookup(unittest.TestCase):
    '''Class to test dns_lookup'''

    def test_bulk_lookup(self):
        input_path = r'input\urls.txt'

        result = dns_lookup.bulk_lookup(input_path)
        self.assertEqual(2, len(result))

    def test_get_ip_from_url(self):
        url = 'google.com'
        result = dns_lookup.get_ip_from_url(url)
        self.assertTrue(result)

    def test_trim_url(self):
        '''Calls dns_lookup.trim_url on multiple urls'''
        ans = 'google.com'
        url_1 = 'http://www.google[.]com/search?q=\"test"'
        url_2 = 'https://google.com/search?q=\"test2"'
        
        result1 = dns_lookup.trim_url(url_1)
        result2 = dns_lookup.trim_url(url_2)

        self.assertEqual(result1, ans)
        self.assertEqual(result2, ans)

if __name__ == "__main__":
    unittest.main()
