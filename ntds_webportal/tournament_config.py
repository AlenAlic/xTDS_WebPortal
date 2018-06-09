from ntds_webportal.values import *
import datetime

# Entry fees in EuroCENTS
STUDENT_PRICE = 8000
NON_STUDENT_PRICE = 9000

# Levels that participate in the tournament
PARTICIPATING_LEVELS = [BREITENSPORT, CLOSED, OPEN_CLASS]

# Levels that have to blind date
BLIND_DATE_LEVELS = [CLOSED, OPEN_CLASS]

# Shirt price in EuroCENTS and shirt sizes
SHIRT_PRICE = 1600
SHIRT_SIZES = {
    'MS': 'Men\'s S',
    'MM': 'Men\'s M',
    'ML': 'Men\'s L',
    'MXL': 'Men\'s XL',
    'MXXL': 'Men\'s XXL',
    'FXS': 'Woman\'s XS',
    'FS': 'Woman\'s S',
    'FM': 'Woman\'s M',
    'FL': 'Woman\'s L',
    'FXL': 'Woman\'s XL',
    'FXXL': 'Woman\'s XXL'
}

# Sticker price in EuroCENTS and type of stickers
STICKER_PRICE = 200
MERCHANDISE = {
    'AliceinWonderland': 'Alice in Wonderland',
    'Avatar': 'Avatar',
    'HarryPotter': 'Harry Potter',
    'IndianaJones': 'Indiana Jones',
    'LordoftheRings': 'Lord of the Rings',
    'Matrix': 'Matrix',
    'PiratesoftheCaribean': 'Pirates of the Caribean',
    'StarTrek': 'Star Trek',
    'StarWars': 'Star Wars'
}

tournament_settings = {
    'levels': PARTICIPATING_LEVELS,
    'blind_date_levels': BLIND_DATE_LEVELS,
    'tournament': ETDS,
    'merchandise_closing_date': int(datetime.datetime(2018, 9, 1, 3, 0, 0, 0).timestamp())
}
