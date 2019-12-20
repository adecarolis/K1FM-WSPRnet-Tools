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
    parser.add_argument('callsign', metavar='callsign', type=str, help='station callsign')
    parser.add_argument('first_identifier', metavar='first_identifier', type=str, choices=['Q', '0'], help='first identifier (Q or 0)')
    parser.add_argument('second_identifier', metavar='second_identifier', type=int, choices=range(0, 10), help='second identifier (0 to 9)')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true')
    parser.add_argument('--debug', dest='debug', action='store_true')
    
    args = parser.parse_args()
    debug = args.debug

    if debug:
        print('Command line arguments:')
        print(args)

    callsign = args.callsign

    pp = pprint.PrettyPrinter(indent=4)
    res = WSPRnet_fetch.get_telemetry(callsign,
                                      args.first_identifier,
                                      args.second_identifier)

    if res is None:
        if debug:
            print('No WSPR data found')
        exit(0)

    if debug:
        print('WSPR Data:')
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

    # At arrival, WSPR data is at least 112 seconds 'old'
    # We have 45 seconds to capture it, otherwise it will be considered
    # expired
    packet_age = res_age.seconds - 112
    if (packet_age) > 45:
        if debug:
            print('No new WSPR data found (age:)', packet_age)
            print('Latest WSPR entry: ', res['datetime'])
        exit(0)

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
    
    if debug:
        print('Raw APRS string being sent: ', aprs_string)
        print('Parsed APRS data being sent:')
        pp.pprint(aprslib.parse(aprs_string))

    if not args.dry_run:
        if debug:
            print('Packet sent to APRS-IS')
        AIS.sendall(aprs_string)
    else:
        if debug:
            print('Dry run! Not sending anything to APRS-IS')

    exit(0)