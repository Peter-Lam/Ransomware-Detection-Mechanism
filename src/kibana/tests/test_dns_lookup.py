#!/usr/bin/python
'''Test file to test dns_lookup'''
import sys
import unittest

sys.path.append('../')
from utils import dns_lookup # pylint: disable=C0413,E0401

class TestDNSLookup(unittest.TestCase):
    '''Class to test dns_lookup'''

    def test_bulk_lookup(self):
        '''Calls dns_lookup.bulk_lookup on a text file'''
        input_path = './input/urls.txt'
        result = dns_lookup.bulk_lookup(input_path)
        self.assertEqual(2, len(result))

    def test_get_ip_from_url(self):
        '''Calls dns_lookup.get_ip_from_url on google'''
        url = 'google.com'
        result = dns_lookup.get_ip_from_url(url)
        self.assertTrue(result)

    def test_trim_url(self):
        '''Calls dns_lookup.trim_url on multiple urls'''
        ans = 'google.com'
        ans2 = 'youtube.com'

        url_1 = 'http://www.google[.]com/search?q=\"test"'
        url_2 = 'https://google.com/search?q=\"test2"'
        url_3 = 'http://youtube.com/'

        result1 = dns_lookup.trim_url(url_1)
        result2 = dns_lookup.trim_url(url_2)
        result3 = dns_lookup.trim_url(url_3)

        self.assertEqual(result1, ans)
        self.assertEqual(result2, ans)
        self.assertEqual(result3, ans2)

if __name__ == "__main__":
    unittest.main()
