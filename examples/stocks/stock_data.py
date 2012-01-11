#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A simple module that acts like a remote db for stock info. """
import time
import datetime
import numpy as np


def datestr2ts(date):
    year, month, day = date.split('-')
    dt = datetime.date(int(year), int(month), int(day))
    return time.mktime(dt.timetuple())


class TickData(object):

    usecols = (2, 3, 4, 5, 6, 7)

    converters = {
        2: datestr2ts,
        3: float,
        4: float,
        5: float,
        6: float,
        7: int,
    }

    dtype = np.dtype([
        ('dates', 'float'), 
        ('open', 'float'), 
        ('high', 'float'),
        ('low', 'float'), 
        ('close', 'float'), 
        ('volume', 'int'),
    ])

    def __init__(self, path):
        self._arr = np.loadtxt(path, dtype=self.dtype, usecols=self.usecols,
                               delimiter=',', converters=self.converters)[::-1]
        
    @property
    def min_date(self):
        return self._arr['dates'][0]
    
    @property
    def max_date(self):
        return self._arr['dates'][-1]
    
    def get_data(self, start, end, numpoints):
        arr = self._arr
        dates = np.linspace(start, end, numpoints)
        out = np.empty((numpoints,), dtype=self.dtype)
        out['dates'] = dates
        indexes = arr['dates']
        out['open'] = np.interp(dates, indexes, arr['open'])
        out['close'] = np.interp(dates, indexes, arr['close'])
        out['low'] = np.interp(dates, indexes, arr['low'])
        out['high'] = np.interp(dates, indexes, arr['high'])
        out['volume'] = np.interp(dates, indexes, arr['volume'])
        return out


_db_symbols = {
    'MSFT': TickData('./demo_support/msft.csv'),
    'AAPL': TickData('./demo_support/aapl.csv'),
    'GOOG': TickData('./demo_support/goog.csv'),
}


def get_symbols():
    return sorted(_db_symbols.keys())


def get_symbol_date_range(symbol):
    tick_data = _db_symbols.get(symbol)
    if not tick_data:
        return
    return (datetime.date.fromtimestamp(tick_data.min_date), 
            datetime.date.fromtimestamp(tick_data.max_date))


def get_data(symbol, start_date, end_date, numpoints):
    tick_data = _db_symbols.get(symbol)
    if not tick_data:
        return
    startts = time.mktime(start_date.timetuple())
    endts = time.mktime(end_date.timetuple())
    return tick_data.get_data(startts, endts, numpoints)

