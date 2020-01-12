import requests
import logging
import json
import unicodedata
from K1FM_WSPRnet_Tools import gridsquare_functions
from K1FM_WSPRnet_Tools import values
from datetime import datetime
from bs4 import BeautifulSoup


def _wspr_request(callsign, timelimit=3600 * 24, band=14, count=50):
    ''' Returns a request object for the WSPRnet page relative to the
        provided callsign / timeframe '''

    url = 'http://wsprnet.org/drupal/wsprnet/spotquery'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Content-Length': '181',
        'Cache-Control': 'max-age=0',
        'Origin': 'http://wsprnet.org',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 '
        'Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
        'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'http://wsprnet.org/drupal/wsprnet/spotquery',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9'}

    payload = {
        'band': band,
        'count': count,
        'call': callsign,
        'reporter': '',
        'timelimit': timelimit,
        'sortby': 'date',
        'sortrev': 1,
        'op': 'Update',
        'form_build_id': 'form-9jnSgxLZlCLHB_6W88KTzk5CNnVWYpXyhd6phQNS4T8',
        'form_id': 'wsprnet_spotquery_form'
    }

    res = requests.post(url, data=payload, headers=headers)
    return res.content


def _parse_wspr_response(response_content):
    ''' Gets the request object of a WSPRnet page and parses it '''

    parsed_html = BeautifulSoup(response_content, features="html.parser")
    main_content = parsed_html.body.find(
        'div', attrs={'class': 'region region-content'})
    table = main_content.find('table')
    table_rows = table.findAll('tr')

    rows = []
    res = []

    for tr in table_rows:
        td = tr.findAll('td')
        row = [i.text.replace("&nbsp;", "") for i in td]
        if len(row) > 0:
            rows.append(row)

    WSPR_datapoint = [
        'datetime',
        'callsign',
        'frequency',
        'snr',
        'drift',
        'grid',
        'pwr',
        'reporter',
        'rgrid',
        'km',
        'az'
    ]

    for row in rows:
        res.append(dict(zip(WSPR_datapoint, [x for x in map(str.strip, row)])))

    return res


def get_telemetry(callsign, letter, number):
    ''' Returns latest telemetry for given callsign provided
        an ID letter (Q or 0) and number (0 to 9) are provided.

        Currently available:

        - Altitude
        - 6 Chars Gridsquare
        - Voltage
        - Temperature
        - Sats


        Encoding:

        case 0 :
        for (i = 0; i < 5; i++ ) {
            g_beacon_callsign[i] = BEACON_CALLSIGN_6CHAR[i];
            if (BEACON_CALLSIGN_6CHAR[i] == '\0') break;
        }
        g_tx_pwr_dbm = encode_altitude(g_tx_data.altitude_m);
        break;

        case 1:
        g_beacon_callsign[0] = BEACON_CHANNEL_ID_1;
        g_beacon_callsign[1] = encode_battery_voltage(voltage);
        g_beacon_callsign[2] = BEACON_CHANNEL_ID_2;
        g_beacon_callsign[3] = g_tx_data.grid_sq_6char[4];
        g_beacon_callsign[4] = g_tx_data.grid_sq_6char[5];
        g_beacon_callsign[5] = encode_temperature(g_tx_data.temperature_c);
        g_tx_pwr_dbm = encode_solar_voltage_sats(0, g_tx_data.number_of_sats);
        '''

    try:
        wspr_regular = _parse_wspr_response(
            _wspr_request(callsign=callsign, count=1))[0]
        search_callsign = '{}%{}*'.format(letter, number)
        wspr_extended = _parse_wspr_response(
            _wspr_request(callsign=search_callsign, count=1))[0]
    except IndexError:
        return None

    res = {}

    if wspr_extended['datetime'] < wspr_regular['datetime']:
        datetime = wspr_regular['datetime']
    else:
        datetime = wspr_extended['datetime']

    res['callsign'] = wspr_regular['callsign']
    res['telemetry_callsign'] = wspr_extended['callsign']
    res['datetime'] = datetime
    res['grid'] = wspr_extended['grid'] + \
        wspr_extended['callsign'][3] + wspr_extended['callsign'][4]

    try:
        res['altitude'] = values.altitude[float(wspr_regular['pwr'])]
    except KeyError:
        res['altitude'] = '?'

    try:
        res['voltage'] = values.voltage[wspr_extended['callsign'][1]]
    except KeyError:
        res['voltage'] = '?'

    try:
        res['temperature'] = values.temperature[wspr_extended['callsign'][5]]
    except KeyError:
        res['temperature'] = '?'

    try:
        res['satellites'] = values.satellites[float(wspr_extended['pwr'])]
    except BaseException:
        res['satellites'] = '?'

    return res
