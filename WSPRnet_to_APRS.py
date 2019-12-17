#!/usr/bin/python
import aprslib
import WSPRnet_fetch
import gridsquare_functions
import pprint

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

    # res = WSPRnet_fetch.get_wspr_data('AA6FT', timelimit=3600, band=14, count=1)
    # if res:
    #     print(res[0])
    callsign = 'N0CALL'
    path = 'WSPR,TCPIP'
    time = '171310z'
    lat, lng = gridsquare_functions.to_latlng('FN30AS')
    lat = decimal_to_aprs(lat, 'lat')
    lng = decimal_to_aprs(lng, 'lng')

    AIS = aprslib.IS(callsign, passwd=aprs_password(callsign), port=14580)
    AIS.connect()

    pp = pprint.PrettyPrinter(indent=4)
    aprs_string = "{}>{}:/{}{}/{:0>9s}>Testing".format(
                                                    callsign,
                                                    path,
                                                    time,
                                                    lat,
                                                    lng
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
