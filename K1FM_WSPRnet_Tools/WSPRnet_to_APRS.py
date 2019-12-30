#!/usr/bin/python
import argparse
import aprslib
from K1FM_WSPRnet_Tools import WSPRnet_fetch
from K1FM_WSPRnet_Tools import gridsquare_functions
import pprint
from datetime import datetime


def aprs_password(callsign):
    ''' Takes a callsign and returns its APRS-IS password '''

    # Credit: Peter Goodhall, https://github.com/magicbug/PHP-APRS-Passcode
    callsign = callsign.upper()
    hash = 0x73e2
    i = 0
    while i < len(callsign):
        hash ^= ord(callsign[i:i+1]) << 8
        hash ^= ord(callsign[i+1:i+2])
        i += 2
    return hash & 0x7fff


def decimal_to_aprs(deg, latlng):
    ''' Converts deciaml lat / lng values to the APRS compatible format '''

    assert latlng == 'lat' or latlng == 'lng'

    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60

    if latlng == 'lat' and d >= 0: suffix = 'N'
    elif latlng == 'lat' and d < 0: suffix = 'S'
    
    if latlng == 'lng' and d >= 0: suffix = 'E'
    elif latlng == 'lng' and d < 0: suffix = 'W'

    return '{}{:0<2d}.{}{}'.format(abs(d), m, int(sd/60*100), suffix)


def AIS_send(aprs_string, callsign):
    ''' Send a properly formatted APRS packet to the APRS-IS network '''

    AIS = aprslib.IS(callsign, passwd=aprs_password(callsign), port=14580)
    AIS.connect()
    AIS.sendall(aprs_string)


def _get_utc_now():
    ''' Helper function that returns the current UTC timestamp '''

    return datetime.utcnow()


def check_data_age(wspr_data):
    ''' Returns the age of a wspr packet '''

    res_datetime = datetime.strptime(wspr_data['datetime'], '%Y-%m-%d %H:%M')
    res_age = _get_utc_now() - res_datetime

    # At arrival, WSPR data is at least 112 seconds 'old'
    return res_age.seconds - 112


def generate_aprs_string(wspr_data):
    ''' Takes WSPR data and generates a corresponding APRS string '''

    res_datetime = datetime.strptime(wspr_data['datetime'], '%Y-%m-%d %H:%M')
    path = 'WSPR,TCPIP'
    time = '{:0>2s}{:0>2s}{:0>2s}'.format(
                            str(res_datetime.day),
                            str(res_datetime.hour),
                            str(res_datetime.minute)
                        )
    alt = int(int(wspr_data['altitude']) * 3.2808)

    lat, lng = gridsquare_functions.to_latlng(wspr_data['grid'])
    lat = decimal_to_aprs(lat, 'lat')
    lng = decimal_to_aprs(lng, 'lng')

    return "{}-11>{}:/{}z{}/{:0>9s}O{} Solar:{}V Temperature:{}C Satellites:{} /A={:0>6d}".format(
                                                    wspr_data['callsign'],
                                                    path,
                                                    time,
                                                    lat,
                                                    lng,
                                                    wspr_data['telemetry_callsign'],
                                                    wspr_data['voltage'],
                                                    wspr_data['temperature'],
                                                    wspr_data['satellites'],
                                                    alt
                                                )