import os
import sys
import csv
import time
import gzip
import shutil
import simplekml
import pycurl
from dateutil.relativedelta import relativedelta
from K1FM_WSPRnet_Tools import gridsquare_functions


def gunzip_shutil(source_filepath, dest_filepath, block_size=65536):
    ''' Expands a gzipped file '''

    with gzip.open(source_filepath, 'rb') as s_file, \
            open(dest_filepath, 'wb') as d_file:
        shutil.copyfileobj(s_file, d_file, block_size)

def progress_bar(total, existing, upload_t, upload_d):
    sys.stdout.write('{0:.1f}'.format(existing / (total + 1) * 100, end=''))
    sys.stdout.flush()
    sys.stdout.write('% ')
    sys.stdout.write('\b\b\b\b\b\b\b\b')
    sys.stdout.flush()


def download_file(url):
    ''' Download a given URL '''

    path = '/tmp/' + os.path.basename(url)

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)

    # Setup writing
    if os.path.exists(path):
        f = open(path, "ab")
        c.setopt(pycurl.RESUME_FROM, os.path.getsize(path))
    else:
        f = open(path, "wb")

    c.setopt(pycurl.WRITEDATA, f)

    #c.setopt(pycurl.VERBOSE, 1) 
    c.setopt(pycurl.NOPROGRESS, 0)
    c.setopt(pycurl.XFERINFOFUNCTION, progress_bar)
    try:
        c.perform()
    except:
        pass

def expand_gzip(path):
    ''' Expand in place a gzipped archive'''

    csv_path = path[0:-3]
    assert path[-3:] == '.gz'

    if not os.path.exists(csv_path):
        gunzip_shutil(path, csv_path)


def extract_data(path, callsign, first_identifier, second_identifier):
    ''' Extract postions from WSPR data '''

    assert path[-4:] == '.csv'

    res = []
    locators = []

    with open(path, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:

            if (row[6] == callsign or (row[6][0] == first_identifier and row[6][2] == str(second_identifier))):
                if (row[6] == callsign):
                    locators.append(row[7])
                    res.append(row)
                else:
                    if (row[7] in locators):
                        res.append(row)
    
    return res

def get_months_list(start_month, end_month):
    ''' Returns the list of months between a start and e end month '''

    assert end_month >= start_month

    months = []
    months.append(start_month)
    while start_month < end_month:
        start_month = start_month + relativedelta(months=1)
        months.append(start_month)
    
    return months

def get_files_list(months):
    ''' Returns the list of files that need to be downloaded given a list of months '''

    assert len(months) > 0

    files = []
    for m in months:
        files.append('wsprspots-' + m.strftime("%Y-%m") + '.csv.gz')
    
    return files


def generate_kml_data(wspr_data):
    ''' 
        Given a list of WSPR datapoints, generates a list
        to be used to generate a KML file:
        Eg.:
        [['FN30AS', datetime, lat, lng], ['FN30AT', datetime, lat, lng]]
    '''
    
    altitude_dict = {
        '0': 500,
        '3': 1000,
        '7': 2000,
        '10': 3000,
        '13': 4000,
        '17': 5000, 
        '20': 6000,
        '23': 7000,
        '27': 8000,
        '30': 9000,
        '33': 10000,
        '37': 11000,
        '40': 12000,
        '43': 13000,
        '47': 14000,
        '50': 15000,
        '53': 16000,
        '57': 17000,
        '60': 18000
    }

    locators_data = {}
    altitude = 0
    for row in wspr_data:
        callsign = row[6]
        epoch = row[1]
        locator_4letters = row[7]
        locator = locator_4letters + callsign[3:5].lower()

        # From regular WSPR frames we just use the Altitude
        if row[6][0] != 'Q' and row[6][0] != '0':
            altitude = altitude_dict[row[8]]
            continue

        datetime = time.localtime(int(epoch))
        lat, lng = gridsquare_functions.to_latlng(locator)
        # Save one datapoint per locator only
        locators_data[locator] = (datetime, lat, lng, altitude)
    
    res = []
    for key in locators_data.keys():
        tmp = []
        tmp.append(key)
        tmp.extend(locators_data[key])
        res.append(tmp)
        
    return res

def _print_time(datetime, str_pattern):
    return time.strftime(str_pattern, datetime)

def save_kml_file(data, filename):
    ''' Saves a list of locator positions as a KML formatted file '''

    kml = simplekml.Kml()
    coords = []
    ls = kml.newlinestring(name=filename)
    tmp = {}

    # Group data by day, so that KML elements can be organized
    # in folders
    for x in sorted(data, key=lambda x: x[1]):
        h_date = time.strftime('%B %d', x[1])
        if h_date in tmp:
            tmp[ h_date ].append(x)
        else:
            tmp[ h_date ] = [x]

    # Create a KML folder for each day. Points within folders are
    # ordered by datetime
    for day_str in sorted(tmp.keys(), key=lambda  x: x[1]):

        fol = kml.newfolder(name=day_str)
        for k in sorted(tmp[day_str], key=lambda x: x[1]):
            coords.append( (k[3], k[2], k[4]) )
            pnt = fol.newpoint( name='{} {} {}m'.format(_print_time(k[1], '%H:%M'),
                                                                    k[0],
                                                                    k[4]),
                                coords=[(k[3],
                                         k[2],
                                         k[4])] )
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
            pnt.altitudemode = 'absolute'
            pnt.description = 'Date/Time:{}<br/>Locator: {}<br/>Altitude: {}m<br/>'.format(_print_time(k[1], '%B %d %Y %H:%M:%s'),
                                                                                                       k[0],
                                                                                                       k[4])
    ls.coords = coords
    ls.altitudemode = simplekml.AltitudeMode.relativetoground

    kml.save(filename + '.kml')