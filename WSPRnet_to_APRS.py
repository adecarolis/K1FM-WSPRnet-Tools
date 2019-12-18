#!/usr/bin/python
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

    callsign = 'K1FM'

    pp = pprint.PrettyPrinter(indent=4)
    res = WSPRnet_fetch.get_telemetry(callsign,'Q',9)
    pp.pprint(res)

    res_datetime = datetime.strptime(res['datetime'], '%Y-%m-%d %H:%M')
    res_age = datetime.utcnow() - res_datetime

    # res = {}

    # res['callsign'] = 'K1FM'
    # res['grid'] = 'FN30AS'
    # res['altitude'] = '10'
    # res['temperature'] = '5'
    # res['voltage'] = '3.1'
    # res_age = 40

    if res == {}:
        exit(1)

    res_datetime = datetime.strptime('2019-12-18 03:18', '%Y-%m-%d %H:%M')

    # if res_age.second > 180:
    #     exit(2)

    path = 'WSPR,TCPIP'
    time = '{:0>2s}{:0>2s}{:0>2s}'.format(
                            str(res_datetime.day),
                            str(res_datetime.hour),
                            str(res_datetime.minute)
                        )
    alt = int(int(res['altitude']) * 3.2808)
    temperature = res['temperature']
    voltage = res['voltage']
    print(time)

    lat, lng = gridsquare_functions.to_latlng(res['grid'])
    lat = decimal_to_aprs(lat, 'lat')
    lng = decimal_to_aprs(lng, 'lng')

    AIS = aprslib.IS(callsign, passwd=aprs_password(callsign), port=14580)
    AIS.connect()

    aprs_string = "{}>{}:/{}z{}/{:0>9s}O{}V {}C /A={:0>6d}".format(
                                                    callsign,
                                                    path,
                                                    time,
                                                    lat,
                                                    lng,
                                                    voltage,
                                                    temperature,
                                                    alt
                                                )
    pp.pprint(aprslib.parse(aprs_string))


    AIS.sendall(aprs_string)

    # callsign = 'K1FM'
    # path = 'APRS64'
    # time = '092345z'
    # gridsquare = '4903.50N/07201.75W'
    # aprs_string = "WC3R>APWW10,TCPIP*,qAC,T2UKRAINE:>FN10jk/- APRSISCE/32"
    # pp.pprint(aprslib.parse(aprs_string.format(
    #                                             callsign,
    #                                             path,
    #                                             time,
    #                                             gridsquare
    #                                           )))

    exit(0)