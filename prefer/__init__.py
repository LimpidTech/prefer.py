__author__ = 'Bailey Stoner <monokrome@monokro.me>'
__version__ = '0.1.0'


import sys


def environment_not_supported():
    raise EnvironmentError(
        'Prefer uses strict typing syntax which requires '
        'Python 3.6 or higher in order to use.'
    )


if int(sys.version[0]) < 3:
    environment_not_supported()

elif int(sys.version[0]) == 3 and int(sys.version[2]) < 6:
    environment_not_supported()

from prefer import loading

load = loading.load
