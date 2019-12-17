import csv
import time
import simplekml
import gridsquare_functions


if __name__ == '__main__':
    with open('test.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')

        positions = {}
        for row in spamreader:
            callsign = row[6]
            epoch = row[1]
            locator_4letters = row[7]
            locator = locator_4letters + callsign[3:5].lower()
            datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(epoch)))
            lat, lng = to_latlng(locator)
            positions[locator] = (datetime, lat, lng)
        
        kml = simplekml.Kml()
        style = simplekml.Style()
        style.labelstyle.color = simplekml.Color.red  # Make the text red
        style.labelstyle.scale = 2  # Make the text twice as big
        style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'

        for locator in positions:
            pnt = kml.newpoint(name=positions[locator][0] + ' - ' + locator, coords=[(positions[locator][2], positions[locator][1])])
            pnt.style = style

        kml.save('test.kml') 