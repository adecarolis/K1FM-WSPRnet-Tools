#!/usr/bin/python
import string

def _lng_to_gridsquare(lng):
    """ Takes in a WGS-84 compatible longitude value and converts it into
    a tuple in the form of (field, square, subsquare). """ 
    lng = lng + 180
    field, lng = divmod(lng, 20)
    square, lng = divmod(lng, 2)
    subsq = (lng * 12)
    return (string.ascii_uppercase[int(field)], int(square), string.ascii_lowercase[int(subsq)])

def _lat_to_gridsquare(lat):
    """ Takes in a WGS-84 compatible latitude value and converts it into
    a tuple in the form of (field, square, subsquare). """ 
    lat = lat + 90
    field, lat = divmod(lat, 10)
    square, lat = divmod(lat, 1)
    subsq = lat * 24
    return (string.ascii_uppercase[int(field)], int(square), string.ascii_lowercase[int(subsq)])

def _to_lat(field, square, subsq=None):
    """ Converts the specified field, square, and (optional) sub-square into a
    WGS-84 compatible latitude value. """
    lat = (string.ascii_uppercase.index(field) * 10.0) - 90
    lat += square
    if subsq is not None:
        lat += (string.ascii_lowercase.index(subsq) / 24.0)
        lat += 1.25 / 60.0 
    else:
        lat += 0.5
    return lat

def _to_lng(field, square, subsq=None):
    """ Converts the specified field, square, and (optional) sub-square into a
    WGS-84 compatible longitude value. """
    lng = (string.ascii_uppercase.index(field) * 20.0) - 180
    lng += square * 2.0
    if subsq is not None:
        lng += string.ascii_lowercase.index(subsq) / 12.0
        lng += 2.5 / 60.0
    else:
        lng += 1.0
    return lng

def to_gridsquare(latitude, longitude):
    """ Takes in a WGS-84 compatible combination of latitude and longitude
    values, and creates the string representation of the Maidenhead location,
    also known as a "gridsquare". """ 
    if not (-180 <= latitude <= 180):
        raise ValueError("Invalid latitude specified.")
    if not (-180 <= longitude <= 180):
        raise ValueError("Invalid longitude specified.")
    lat = _lat_to_gridsquare(latitude)
    lng = _lng_to_gridsquare(longitude)
    return "".join([str(x) + str(y) for x, y in zip(lng,lat)])

def to_latlng(gs):
    """ Takes in a Maidenhead locator string (gridsquare) and converts it into
    a tuple of WGS-84 compatible (latitude, longitude). """
    if len(gs) < 4:
        raise ValueError("Invalid gridsquare specified.")
    lat, lng = None, None
    if len(gs) > 4:
        lng = _to_lng(gs[0], int(gs[2]), gs[4].lower())
        lat = _to_lat(gs[1], int(gs[3]), gs[5].lower())
    else:
        lng = _to_lng(gs[0], int(gs[2]))
        lat = _to_lat(gs[1], int(gs[3]))
    return round(lat, 3), round(lng, 3)