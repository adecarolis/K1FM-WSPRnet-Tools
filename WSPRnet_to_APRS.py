#!/usr/bin/python
import argparse
import aprslib
import WSPRnet_fetch
import gridsquare_functions
import pprint
from datetime import datetime


def aprs_password(callsign):
    ''' Takes a callsign and returns its APRS-IS password '''

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='WSPR to APRS gateway bridge for K1FM Picoballoon boards.')
    parser.add_argument('callsign', metavar='callsign', type=str, help='station callsign')
    parser.add_argument('first_identifier', metavar='first_identifier', type=str, choices=['Q', '0'], help='first identifier (Q or 0)')
    parser.add_argument('second_identifier', metavar='second_identifier', type=int, choices=range(0, 10), help='second identifier (0 to 9)')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true')
    parser.add_argument('--max-age', default = 45, dest='max_age', type=int,  help='number of seconds after a WSPR packet is considered as expired')
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
    
    age = check_data_age(res)

    if (age < args.max_age):
        aprs_string = generate_aprs_string(res)
    else:
        if debug:
            print('No new WSPR data found (last packet age: {}s)'.format(age))
            print('Latest WSPR entry: ', res['datetime'])
        exit(0)
    
    if debug:
        print('Raw APRS string being sent: ', aprs_string)
        print('Parsed APRS data being sent:')
        pp.pprint(aprslib.parse(aprs_string))

    if not args.dry_run:
        if debug:
            print('Packet sent to APRS-IS')
        AIS_send(aprs_string, callsign)
    else:
        if debug:
            print('Dry run! Not sending anything to APRS-IS')

    exit(0)