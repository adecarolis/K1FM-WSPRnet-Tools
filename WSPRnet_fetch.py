import requests
import logging
import json
import unicodedata
import gridsquare_functions
from bs4 import BeautifulSoup

def get_wspr_data(callsign, timelimit = 3600, band = 14, count = 50):
    ''' Returns a list of lists with WSPR entries for the provided callsign in the provided timeframe '''

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

    url = 'http://wsprnet.org/drupal/wsprnet/spotquery'

    headers = {
        'Content-Type'              : 'application/x-www-form-urlencoded',
        'Connection'                : 'keep-alive',
        'Content-Length'            : '181',
        'Cache-Control'             : 'max-age=0',
        'Origin'                    : 'http://wsprnet.org',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent'                : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Accept'                    : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer'                   : 'http://wsprnet.org/drupal/wsprnet/spotquery',
        'Accept-Encoding'           : 'gzip, deflate',
        'Accept-Language'           : 'en-US,en;q=0.9'
    }

    payload = {
        'band'          : band,
        'count'         : count,
        'call'          : callsign,
        'reporter'      : '',
        'timelimit'     : timelimit,
        'sortby'        : 'date',
        'sortrev'       : 1,
        'op'            : 'Update',
        'form_build_id' : 'form-9jnSgxLZlCLHB_6W88KTzk5CNnVWYpXyhd6phQNS4T8',
        'form_id'       : 'wsprnet_spotquery_form'
    }

    response = requests.post(url, data=payload, headers=headers)
    #print(response)
    parsed_html = BeautifulSoup(response.content, features="html.parser")
    #print(parsed_html)
    main_content = parsed_html.body.find('div', attrs={'class':'region region-content'})
    #print(main_content)
    table = main_content.find('table')
    table_rows = table.findAll('tr')

    rows = []
    res = []

    for tr in table_rows:
        td = tr.findAll('td')
        row = [i.text.replace("&nbsp;", "") for i in td]
        if len(row) > 0:
            rows.append(row)
    
    for row in rows:
        res.append( dict( zip(WSPR_datapoint, [ x for x in map(str.strip, row)]) ) )
    
    return res

def get_telemetry(callsign, letter, number):
    ''' Returns latest telemetry for given callsign provided
        an ID letter (Q or 0) and number (0 to 9) are provided
    
        switch (msg_type) {
        case 0 :
        for (i = 0; i < 5; i++ ) {
        g_beacon_callsign[i] = BEACON_CALLSIGN_6CHAR[i];
        if (BEACON_CALLSIGN_6CHAR[i] == '\0') break;
        }
        g_tx_pwr_dbm = encode_altitude(g_tx_data.altitude_m);
        break;
        
        case 1:
        g_beacon_callsign[0] = BEACON_CHANNEL_ID_1;
        g_beacon_callsign[1] = encode_battery_voltage(g_tx_data.battery_voltage_v_x10);
        g_beacon_callsign[2] = BEACON_CHANNEL_ID_2;
        g_beacon_callsign[3] = g_tx_data.grid_sq_6char[4];
        g_beacon_callsign[4] = g_tx_data.grid_sq_6char[5];
        g_beacon_callsign[5] = encode_temperature(g_tx_data.temperature_c);

        g_tx_pwr_dbm = encode_solar_voltage_sats(0, g_tx_data.number_of_sats); // TDB: This can be utilized better
        break; '''
    
    wspr_regular  = get_wspr_data(callsign=callsign, count = 1)[0]
    wspr_extended = get_wspr_data(callsign='{}%{}*'.format(letter, number), count = 1)[0]

    for d in wspr_extended:
        if d.grid != wspr_regular.grid:
            wspr_extended.delete(d)

    # TODO: get real data
    dbm_callsign = '23'
    dbm_telemetry = '17'
    telemetry = 'QB8BII'
    locator_4 = 'EK67'
    
    return dbm_callsign, dbm_telemetry, telemetry, locator_4


def parse_wspr_telemetry(callsign, letter, number):
    ''' Parses an extended telemetry WSPR frame and returns
        locator, altitude, temperature, voltage '''

    temperature = {
        0: 35,
        3: 32,
        7: 27,
        10: 22,
        13: 17,
        17: 12,
        20: 7,
        23: 2,
        27: -3,
        30: -8,
        33: -13,
        37: -18,
        40: -23,
        43: -28,
        47: -33,
        50: -38,
        53: -43,
        57: -48,
        60: -50
    }

    altitude = {
        0: 500,
        3: 1500,
        7: 2500,
        10: 3500,
        13: 4500,
        17: 5500,
        20: 6500,
        23: 7500,
        27: 8500,
        30: 9500,
        33: 10500,
        37: 11500,
        40: 12500,
        43: 13500,
        47: 14500,
        50: 15500,
        53: 16500,
        57: 17500,
        60: 18000
    }

    dbm_callsign, dbm_telemetry, telemetry, locator_4 = latest_wspr_entry(callsign, letter, number)
    locator = locator_4 + telemetry[3:5].lower()
    altitude = altitude[dbm_callsign]
    #speed = get_speed(dbm_telemetry)
    temperature = temperature[telemetry[5]]
    
    return locator, altitude, 0, temperature, voltage
