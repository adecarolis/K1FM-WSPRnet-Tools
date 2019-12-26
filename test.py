import pprint
import aprslib
import WSPRnet_to_APRS
import unittest
import mock
from datetime import datetime

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
        self.assertEqual('N0CALL-11>WSPR,TCPIP:/230200z4033.71N/01520.51EOSolar:3.1V Temperature:5C Satellites:2 /A=001640',
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