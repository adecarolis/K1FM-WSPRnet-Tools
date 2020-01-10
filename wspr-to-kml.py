#!/usr/bin/python

import argparse
import os
from datetime import datetime
from K1FM_WSPRnet_Tools import WSPRnet_to_kml


def year_month_type(arg_value):
    try:
        year_month = datetime.strptime(arg_value, '%Y-%m')
    except BaseException:
        raise argparse.ArgumentTypeError
    return year_month


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='This utility takes data from WSPR archives and generates KML files for K1FM Picoballoon flights.')
    parser.add_argument(
        'callsign',
        metavar='callsign',
        type=str,
        help='balloon callsign')
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
    parser.add_argument(
        '--start-month',
        type=year_month_type,
        dest='start_month',
        help='year-month when the flight begun (eg. 2019-09). Defaults to current month')
    parser.add_argument(
        '--end-month',
        type=year_month_type,
        dest='end_month',
        help='year-month when the flight ended (eg. 2019-11). Defaults to current month')
    parser.add_argument(
        '--skip-downloads',
        dest='skip_downloads',
        action='store_true')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--cleanup', dest='cleanup', action='store_true')

    args = parser.parse_args()
    debug = args.debug

    if not args.start_month:
        args.start_month = datetime.now()

    if args.end_month:
        if args.end_month < args.start_month:
            print('Error: end_month must be greater or equal to start_month')
            exit(1)
    else:
        args.end_month = datetime.now()

    # get the list of the necessary files
    months = WSPRnet_to_kml.get_months_list(args.start_month, args.end_month)
    files = WSPRnet_to_kml.get_files_list(months)

    url_base = 'http://wsprnet.org/archive/'
    path_base = '/tmp/'

    if not args.skip_downloads:
        # Download the necessary files first
        for n in files:
            url = url_base + n

            if debug:
                print('Downloading ', url)

            WSPRnet_to_kml.download_file(url)

    if not args.skip_downloads:
        # Expand the downloaded file
        for n in files:
            path = os.path.join(path_base, n)

            if debug:
                print('Expanding ', path)

            WSPRnet_to_kml.expand_gzip(path)

    # Extract data from the files
    wspr_data = []
    for n in files:
        path = os.path.join(path_base, n)
        csv_path = path[0:-3]

        if debug:
            print('Extracting data from: ', os.path.basename(csv_path))

        res = WSPRnet_to_kml.extract_data(
            csv_path,
            args.callsign,
            args.first_identifier,
            args.second_identifier)

        wspr_data.extend(res)

    res = WSPRnet_to_kml.generate_kml_data(wspr_data)
    filename = args.callsign + '_' + \
        '_'.join([m.strftime("%Y-%m") for m in months])
    if debug:
        print('Writing KML file: {}.kml'.format(filename))
    WSPRnet_to_kml.save_kml_file(res, filename)

    if args.cleanup:
        # Cleanup temporary files
        for n in files:
            if debug:
                print('Cleaning up temporary files')
            path = os.path.join(path_base, n)
            csv_path = path[0:-3]
            os.remove(path)
            os.remove(csv_path)
