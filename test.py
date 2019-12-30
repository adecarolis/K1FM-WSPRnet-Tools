import pprint
import aprslib
import WSPRnet_to_APRS
import WSPRnet_fetch
import unittest
import mock
import requests
import requests_mock
import pickle
from datetime import datetime

class Test_WSPRnet_fetch(unittest.TestCase):

    def test_parse_wspr_response(self):
        res = [
            {'datetime': '2019-12-26 19:46', 
             'callsign': 'N0CALL',
             'frequency': '14.097069',
             'snr': '-10',
             'drift': '0',
             'grid': 'FL08ju',
             'pwr': '10',
             'reporter': 'N0CAL',
             'rgrid': 'FN12gx',
             'km': '1578',
             'az': '5'}
            ]
        pickle_off = open("N0CALL","rb")
        response_content = pickle.load(pickle_off)
        pickle_off.close()
        self.assertEqual(WSPRnet_fetch._parse_wspr_response(response_content), res)
    
    def test_get_telemetry(self):
        with requests_mock.mock() as m:
            res = {
                'callsign': 'SC1ALB',
                'telemetry_callsign': 'SC1ALB',
                'datetime': '2019-12-30 09:30',
                'grid': 'HL25AL',
                'altitude': 11500,
                'voltage': 3.3,
                'temperature': -32,
                'satellites': '?'}
            response = open('response.txt', 'r')
            # Need to figure how to set different responses for different data params
            m.post('http://wsprnet.org/drupal/wsprnet/spotquery', text=response.read())
            response.close()
            self.assertEqual(WSPRnet_fetch.get_telemetry('N0CALL', 'Q', 1), res)


class Test_WSPRnet_to_APRS(unittest.TestCase):

    path = 'WSPR,TCPIP'
    res = {
        'altitude': 500,
        'callsign': 'N0CALL',
        'telemetry_callsign': 'QB9MNJ',
        'datetime': '2019-12-23 02:00',
        'grid': 'JN70MN',
        'satellites': 2,
        'temperature': 5,
        'voltage': 3.1
    }

    def test_aprs_string(self):
        self.assertEqual('N0CALL-11>WSPR,TCPIP:/230200z4033.71N/01520.51EOQB9MNJ Solar:3.1V Temperature:5C Satellites:2 /A=001640',
                         WSPRnet_to_APRS.generate_aprs_string(self.res))
    

    def test_check_data_age(self):
        with mock.patch('WSPRnet_to_APRS._get_utc_now', return_value=datetime(2019, 12, 23, 2, 3, 2)):
            self.assertEqual(70, WSPRnet_to_APRS.check_data_age(self.res))
    
    def test_aprs_password(self):
        self.assertEqual(WSPRnet_to_APRS.aprs_password('N0CALL'), 13023)
    
    def test_decimal_to_aprs(self):
        self.assertEqual(WSPRnet_to_APRS.decimal_to_aprs(40.56, 'lat'), '4033.60N')
        self.assertEqual(WSPRnet_to_APRS.decimal_to_aprs(40.56, 'lng'), '4033.60E')


if __name__ == '__main__':
    unittest.main()