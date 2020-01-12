#!/usr/bin/python

altitude = {
    0.001: 500,  # 0dBm
    0.002: 1500,  # 3dBm
    0.005: 2500,  # 7dBm
    0.01: 3500,  # 10dBm
    0.02: 4500,  # 13dBm
    0.05: 5500,  # 17dBm
    0.1: 6500,   # 20dBm
    0.2: 7500,   # 23dBm
    0.5: 8500,   # 27dBm
    1: 9500,     # 30dBm
    2: 10500,    # 33dBm
    5: 11500,    # 37dBm
    10: 12500,   # 40dBm
    20: 13500,   # 43dBm
    50: 14500,   # 47dBm
    100: 15500,  # 50dBm
    200: 16500,  # 53dBm
    500: 17500,  # 57dBm
    1000: 18000  # 60dBm
}

altitude_dbm = {
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

temperature = {
    'A': -35,
    'B': -32,
    'C': -27,
    'D': -22,
    'E': -17,
    'F': -12,
    'G': -7,
    'H': -2,
    'I': 3,
    'J': 5
}

voltage = {
    'A': 3.0,
    'B': 3.1,
    'C': 3.3,
    'D': 3.5,
    'E': 3.7,
    'F': 3.9,
    'G': 4.1,
    'H': 4.3,
    'I': 4.5,
    'J': 4.7,
    'K': 4.9,
    'L': 5.1
}

satellites = {
    0.001: 2,   # 0dBm
    0.002: 5,   # 3dBm
    0.005: 7    # 7dBm
}