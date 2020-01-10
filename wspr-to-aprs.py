#!/usr/bin/python

import argparse
import pprint
import aprslib
from K1FM_WSPRnet_Tools import WSPRnet_fetch
from K1FM_WSPRnet_Tools import WSPRnet_to_APRS


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='WSPR to APRS gateway bridge for K1FM Picoballoon boards.')
    parser.add_argument(
        'callsign',
        metavar='callsign',
        type=str,
        help='station callsign')
    parser.add_argument(
        'first_identifier',
        metavar='first_identifier',
        type=str,
        choices=[
            'Q',
            '0'],
        help='first identifier (Q or 0)')
    parser.add_argument(
        'second_identifier',
        metavar='second_identifier',
        type=int,
        choices=range(
            0,
            10),
        help='second identifier (0 to 9)')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true')
    parser.add_argument(
        '--max-age',
        default=45,
        dest='max_age',
        type=int,
        help='number of seconds after a WSPR packet is considered as expired')
    parser.add_argument('--debug', dest='debug', action='store_true')

    args = parser.parse_args()
    debug = args.debug

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

    age = WSPRnet_to_APRS.check_data_age(res)

    if (age < args.max_age):
        aprs_string = WSPRnet_to_APRS.generate_aprs_string(res)
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
        WSPRnet_to_APRS.AIS_send(aprs_string, callsign)
    else:
        if debug:
            print('Dry run! Not sending anything to APRS-IS')

    exit(0)
