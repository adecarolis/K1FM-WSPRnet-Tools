# K1FM WSPRnet Tools

This toolset manipulates WSPR data producted by K1FM PicoBalloon boards. Two features are currently implemented:

- WSPR to APRS Gateway

  Allows WSPR data to be fetched, analyzed and re-published to the APRS-IS network.

  ```
  $ ./wspr-to-aprs.py -h
  usage: wspr-to-aprs.py [-h] [--dry-run] [--max-age MAX_AGE] [--debug]
                         callsign first_identifier second_identifier

  WSPR to APRS gateway bridge for K1FM Picoballoon boards.

  positional arguments:
    callsign           station callsign
    first_identifier   first identifier (Q or 0)
    second_identifier  second identifier (0 to 9)

  optional arguments:
    -h, --help         show this help message and exit
    --dry-run
    --max-age MAX_AGE  number of seconds after a WSPR packet is considered as
                       expired
    --debug
  ```

  Example Usage:

  ```
  $ ./wspr-to-aprs.py N0CALL Q 9
  ```

- KML file geneator
  Allows the the creation of KML files from historic WSPR archives.
  
   ```
  $ ./wspr-to-kml.py -h
  usage: wspr-to-kml.py [-h] [--start-month START_MONTH] [--end-month END_MONTH]
                        [--skip-downloads] [--debug] [--cleanup]
                        callsign first_identifier second_identifier
  
  This utility takes data from WSPR archives and generates KML files for K1FM
  Picoballoon flights.
  
  positional arguments:
    callsign              balloon callsign
    first_identifier      first identifier (Q or 0)
    second_identifier     second identifier (0 to 9)
  
  optional arguments:
    -h, --help            show this help message and exit
    --start-month START_MONTH
                          year-month when the flight begun (eg. 2019-09).
                          Defaults to current month
    --end-month END_MONTH
                          year-month when the flight ended (eg. 2019-11).
                          Defaults to current month
    --skip-downloads
    --debug  --cleanup
   ```

  Example Usage:

  ```
  ./wspr-to-kml.py K1FM Q 9 \
    --debug \
    --start-month 2019-12 \
    --end-month 2019-12 \
    --cleanup
  ```




