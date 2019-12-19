#!/usr/bin/python
import argparse
import aprslib
import WSPRnet_fetch
import gridsquare_functions
import pprint
from datetime import datetime

def aprs_password(callsign):
    callsign = callsign.upper()
    hash = 0x73e2
    i = 0
    while i < len(callsign):
        hash ^= ord(callsign[i:i+1]) << 8
        hash ^= ord(callsign[i+1:i+2])
        i += 2
    return hash & 0x7fff


def decimal_to_aprs(deg, latlng):
    assert latlng == 'lat' or latlng == 'lng'

    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60

    if latlng == 'lat' and d >= 0: suffix = 'N'
    elif latlng == 'lat' and d < 0: suffix = 'S'
    
    if latlng == 'lng' and d >= 0: suffix = 'E'
    elif latlng == 'lng' and d < 0: suffix = 'W'

    return '{}{}.{}{}'.format(abs(d), m, int(sd/60*100), suffix)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='WSPR to APRS gateway bridge for K1FM Picoballoon boards.')
    parser.add_argument('callsign', metavar='C', type=str, nargs='+',
                    help='station callsign')
    parser.add_argument('first_identifier', metavar='F', type=str, choices=['Q', '0'], help='first identifier (Q or 0)')
    parser.add_argument('second_identifier', metavar='S', type=int, choices=range(0, 10), help='second identifier (0 to 9)')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--ssid', dest='ssid', type=int, default=None)
    
    args = parser.parse_args()
    print(args)

    callsign = args.callsign

    pp = pprint.PrettyPrinter(indent=4)
    res = WSPRnet_fetch.get_telemetry(callsign,'Q',9)

    if res is None:
        print('No WSPR data found')
        exit(1)

    pp.pprint(res)

    res_datetime = datetime.strptime(res['datetime'], '%Y-%m-%d %H:%M')
    #res_datetime = datetime.strptime('2019-12-19 10:22', '%Y-%m-%d %H:%M')
    res_age = datetime.utcnow() - res_datetime

    # res = {}
    # res['callsign'] = 'K1FM'
    # res['grid'] = 'FN30AS'
    # res['altitude'] = '10'
    # res['temperature'] = '5'
    # res['voltage'] = '3.1'
    # res['satellites'] = 7

    if res_age.seconds > 180:
        print('No new WSPR data found')
        print('Latest WSPR entry: ', res['datetime'])
        exit(1)

    path = 'WSPR,TCPIP'
    time = '{:0>2s}{:0>2s}{:0>2s}'.format(
                            str(res_datetime.day),
                            str(res_datetime.hour),
                            str(res_datetime.minute)
                        )
    alt = int(int(res['altitude']) * 3.2808)

    lat, lng = gridsquare_functions.to_latlng(res['grid'])
    lat = decimal_to_aprs(lat, 'lat')
    lng = decimal_to_aprs(lng, 'lng')

    AIS = aprslib.IS(callsign, passwd=aprs_password(callsign), port=14580)
    AIS.connect()

    aprs_string = "{}>{}:/{}z{}/{:0>9s}OSolar:{}V Temperature:{}C Satellites:{} /A={:0>6d}".format(
                                                    callsign,
                                                    path,
                                                    time,
                                                    lat,
                                                    lng,
                                                    res['voltage'],
                                                    res['temperature'],
                                                    res['satellites'],
                                                    alt
                                                )
    pp.pprint(aprslib.parse(aprs_string))

    AIS.sendall(aprs_string)

    exit(0)