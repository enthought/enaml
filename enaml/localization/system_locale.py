#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime
import locale
import sys
import time

from .abstract_locale import AbstractLocale


# nl_langinfo is not available on Windows and as a result locale is 
# mostly useless. So we have to fake a bunch of stuff for that platform
# and just hard-code it to the english equivalents. 
_win_defaults = {
    'am': 'AM',
    'pm': 'PM',
    'months': {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    },
    'ab_months': {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec',
    },
    'days': {
        1: 'Sunday',
        2: 'Monday',
        3: 'Tuesday',
        4: 'Wednesday',
        5: 'Thursday',
        6: 'Friday',
        7: 'Saturday',
    },
    'ab_days': {
        1: 'Sun',
        2: 'Mon',
        3: 'Tue',
        4: 'Wed',
        5: 'Thu',
        6: 'Fri',
        7: 'Sat',
    },
    'time': '%I:%M:%S %p',
    'ab_time': '%H:%M:%S',
    'date': '%m/%d/%Y',
    'datetime': '%a %b %e %X %Y',
}


def _convert_base(value, base):
    """ Convert a base10 integral number into a string represented in
    a different number base. Bases from 2-36 inclusive are supported.
    
    """
    if not isinstance(value, (int, long)):
        msg = 'Expected integral number type. Got %s instead.'
        raise TypeError(msg % type(value))
    
    if not isinstance(base, int):
        msg = 'Expected integer base. Got %d instead.'
        raise TypeError(msg % base)

    if base < 2 or base > 36:
        msg = 'Base must be between 2 and 36 inclusive. Got %d instead.'
        raise ValueError(msg % base)
    
    digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    parts = []
    push = parts.append
    
    prefix = False
    if value < 0:
        prefix = True
        value = abs(value)
    
    div = divmod
    while value != 0:
        value, mod = div(value, base)
        push(digits[mod])
    
    if prefix:
        push('-')

    return ''.join(reversed(parts))


class SystemLocale(AbstractLocale):
    """ A concrete implementation of AbstractLocale which uses the Python
    'locale' module for locale-related information. 

    The SystemLocale does not maintain any state and will always reflect 
    the current system locale information as given by the 'locale' module.

    """
    @classmethod
    def default(cls):
        """ Initializes the system locale if not already initialized and
        returns an instance of SystemLocale.

        """
        loc = locale.getlocale()
        if loc == (None, None):
            locale.setlocale(locale.LC_ALL, '')
        return cls()
    
    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def name(self):
        """ The RFC 1766 language code for the locale.

        """
        return unicode(locale.getlocale()[0])

    @property
    def encoding(self):
        """ The encoding for strings in the locale.

        """
        return unicode(locale.getlocale()[1])
                
    @property
    def am_string(self):
        """ The string for "AM" time in the locale.

        """
        if sys.platform == 'win32':
            r = _win_defaults['am']
        else:
            r = locale.nl_langinfo(locale.AM_STR)
        return unicode(r)
    
    @property
    def pm_string(self):
        """ The string for "PM" time in the locale.

        """
        if sys.platform == 'win32':
            r = _win_defaults['pm']
        else:
            r = locale.nl_langinfo(locale.PM_STR)
        return unicode(r)

    @property
    def decimal_point(self):
        """ The decimal separator for the locale.

        """
        return unicode(locale.localeconv()['decimal_point'])
            
    @property
    def monetary_decimal_point(self):
        """ The decimal separator for monetary values for the locale.

        """
        return unicode(locale.localeconv()['mon_decimal_point'])

    @property
    def exponential(self):
        """ The exponential character for the locale.

        """
        # Symbol not provided by locale module, so use Python default
        return u'e'

    @property
    def thousands_separator(self):
        """ The thousands separator for the locale.

        """
        return unicode(locale.localeconv()['thousands_sep'])
    
    @property
    def monetary_thousands_separator(self):
        """ The thousands separator for monetary values for the locale.

        """
        return unicode(locale.localeconv()['mon_thousands_sep'])

    @property
    def negative_sign(self):
        """ The monetary negative sign for the locale.

        """
        return unicode(locale.localeconv()['negative_sign'])
                
    @property
    def positive_sign(self):
        """ The monetary positive sign for the locale.

        """
        return unicode(locale.localeconv()['positive_sign'])
            
    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------
    def month_name(self, month_int, abbreviated=False):
        """ The month name for the given month integer.

        Parameters
        ----------
        month_int : int
            An integer in the range 1 to 12 inclusive.
        
        abbreviated : bool, optional
            If True, return the abbreviate version of the month name.
            The default is False.
        
        Returns
        -------
        result : string
            The month name or an empty string in the month int is out
            of range.

        """
        if month_int < 1 or month_int > 12:
            return ''
        if sys.platform == 'win32':
            if abbreviated:
                key = 'ab_months'
            else:
                key = 'months'
            r = _win_defaults[key][month_int]
        else:
            prefix = 'AB' if abbreviated else ''
            attr = prefix + ('MON_%i' % month_int)
            flag = getattr(locale, attr)
            r = locale.nl_langinfo(flag)
        return unicode(r)

    def day_name(self, day_int, abbreviated=False):
        """ The day name for the given day integer.

        Parameters
        ----------
        day_int : int
            An integer in the range 1 to 7 inclusive.
        
        abbreviated : bool, optional
            If True, return the abbreviate version of the day name.
            The default is False.
        
        Returns
        -------
        result : string
            The day name or an empty string in the day int is out
            of range.

        """
        if day_int < 1 or day_int > 7:
            return ''
        if sys.platform == 'win32':
            if abbreviated:
                key = 'ab_days'
            else:
                key = 'days'
            r = _win_defaults[key][day_int]
        else:
            prefix = 'AB' if abbreviated else ''
            attr = prefix + ('DAY_%i' % day_int)
            flag = getattr(locale, attr)
            r = locale.nl_langinfo(flag)
        return unicode(r)
        
    def time_format(self, abbreviated=False):
        """ The format string for a time value.

        Parameters
        ----------
        abbreviated : bool, optional
            If True, return the abbreviate version of the time format.
            The defaults is False.

        Returns
        -------
        result : string
            The time format string.

        """
        if sys.platform == 'win32':
            if abbreviated:
                key = 'ab_time'
            else:
                key = 'time'
            r = _win_defaults[key]
        else:
            flag = locale.T_FMT if abbreviated else locale.T_FMT_AMPM
            r = locale.nl_langinfo(flag)
        return unicode(r)

    def date_format(self, abbreviated=False):
        """ The format string for a date value.

        Parameters
        ----------
        abbreviated : bool, optional
            If True, return the abbreviated version of the date format.
            The defaults is False.

        Returns
        -------
        result : string
            The date format string.
        
        Notes
        -----
        Python's builtin locale (based on langinfo) does not distinguish
        abbreviated and non-abbreviated date formats. So the keyword
        argument is ignored in this implementation.

        """
        if sys.platform == 'win32':
            r = _win_defaults['date']
        else:
            # Python doesn't support %e in strptime, but %d is equivalent
            r = locale.nl_langinfo(locale.D_FMT).replace('%e', '%d')
        return unicode(r)

    def datetime_format(self, abbreviated=False):
        """ The format string for a datetime value.

        Parameters
        ----------
        abbreviated : bool, optional
            If True, return the abbreviated version of the datetime
            format. The defaults is False.

        Returns
        -------
        result : string
            The datetime format string.

        Notes
        -----
        Python's builtin locale (based on langinfo) does not distinguish
        abbreviated and non-abbreviated datetime formats. So the keyword
        argument is ignored in this implementation.

        """
        if sys.platform == 'win32':
            r = _win_defaults['datetime']
        else:
            # Python doesn't support %e in strptime, but %d is equivalent
            r = locale.nl_langinfo(locale.D_T_FMT).replace('%e', '%d')
        return unicode(r)
        
    #--------------------------------------------------------------------------
    # Conversions
    #--------------------------------------------------------------------------
    def to_time(self, time_str, abbreviated=False):
        """ Parse the given time string into a datetime.time object.

        Parameters
        ----------
        time_str : string
            A string formatted according to time_format().

        abbreviated : bool, optional
            Whether or not the time string is using the abbreviated 
            format. The default is False.
        
        Returns
        -------
        result : datetime.time
            The datetime.time object for the string.

        """
        fmt = self.time_format(abbreviated)
        struct_time = time.strptime(time_str, fmt)
        return datetime.time(*struct_time[3:6])

    def to_date(self, date_str, abbreviated=False):
        """ Parse the date string into a datetime.date object.

        Parameters
        ----------
        date_str : string
            A string formatted according to date_format().

        abbreviated : bool, optional
            Whether or not the date string is using the abbreviated 
            format. The default is False.
        
        Returns
        -------
        result : datetime.date
            The datetime.date object for the string.

        """
        fmt = self.date_format(abbreviated)
        struct_time = time.strptime(date_str, fmt)
        return datetime.date(*struct_time[0:3])
    
    def to_datetime(self, datetime_str, abbreviated=False):
        """ Parse the datetime string into a datetime.datetime object.

        Parameters
        ----------
        datetime_str : string
            A string formatted according to datetime_format().

        abbreviated : bool, optional
            Whether or not the datetime string is using the abbreviated 
            format. The default is False.
        
        Returns
        -------
        result : datetime.datetime
            The datetime.datetime object for the string.

        """
        fmt = self.datetime_format(abbreviated)
        struct_time = time.strptime(datetime_str, fmt)
        return datetime.datetime(*struct_time[:6])

    def to_int(self, int_str, base=10):
        """ Parse the string into an integer using the given base.

        Parameters
        ----------
        int_str : string
            The string representing the integer.
        
        base : int, optional
            The number base to use when parsing the string. The valid
            values are the same as those passed to Python's builtin 
            'int'. The default is 10.
        
        Returns
        -------
        result : int
            The parsed integer.

        """
        func = lambda val: int(val, base)
        return locale.atof(int_str, func)
    
    def to_long(self, long_str, base=10):
        """ Parse the string into a long integer using the given base.

        Parameters
        ----------
        long_str : string
            The string representing the integer.
        
        base : int, optional
            The number base to use when parsing the string. The valid
            values are the same as those passed to Python's builtin 
            'int'. The default is 10.
        
        Returns
        -------
        result : long
            The parsed long integer.

        """ 
        func = lambda val: long(val, base)
        return locale.atof(long_str, func)

    def to_float(self, float_str):
        """ Parse the given string into a float.

        Parameters
        ----------
        float_str : string
            The string representing the float.
        
        Returns
        -------
        result : float
            The parsed float.

        """
        return locale.atof(float_str)

    def to_complex(self, complex_str):
        """ Parse the given string into a complex.

        Parameters
        ----------
        complex_str : string
            The string representing the complex.
        
        Returns
        -------
        result : complex
            The parsed complex.

        """
        text = complex_str.replace(self.thousands_separator, u'')
        text = text.replace(self.decimal_point, u'.')
        return complex(text)

    def to_currency(self, currency_str, symbol=True, group=False, intl=False):
        """ Parse the given currency string into a float.

        Parameters
        ----------
        currency_str : string
            The string representing the currency.
        
        symbol : bool, optional
            If True, the currency symbol is included in the string. The
            default is True.
        
        group : bool, optional
            If True, the grouping marks are included in the string. The
            default is False.
        
        intl : bool, optional
            If True, the international version of the currency symbol
            is used in the string. This is only used if 'symbol' is
            True. The default is False.

        Returns
        -------
        result : float
            The parsed float.

        """
        curr = currency_str
        conv = locale.localeconv()
        if symbol:
            if intl:
                curr = curr.replace(conv['int_curr_symbol'], '')
            else:
                curr = curr.replace(conv['currency_symbol'], '')
        if group:
            curr = curr.replace(conv['mon_thousands_sep'], '')
        curr = curr.replace(conv['mon_decimal_point'], '.').strip()
        return float(curr)

    def from_time(self, time_obj, abbreviated=False):
        """ Convert the given time object into a locale specific string.

        Parameters
        ----------
        time_obj : datetime.time
            The time object for conversion.
        
        abbreviated : bool, optional
            Whether or not the time string should use the abbreviated 
            format. The default is False.

        Returns
        -------
        result : unicode string
            The locale formatted time string.

        """
        return unicode(time_obj.strftime(self.time_format(abbreviated)))
    
    def from_date(self, date_obj, abbreviated=False):
        """ Convert the given date object into a locale specific string.

        Parameters
        ----------
        date_obj : datetime.date
            The date object for conversion.
        
        abbreviated : bool, optional
            Whether or not the date string should use the abbreviated 
            format. The default is False.

        Returns
        -------
        result : unicode string
            The locale formatted date string.

        """
        return unicode(date_obj.strftime(self.date_format(abbreviated)))
    
    def from_datetime(self, datetime_obj, abbreviated=False):
        """ Convert the given datetime object into a locale specific 
        string.

        Parameters
        ----------
        datetime_obj : datetime.datetime
            The datetime object for conversion.
        
        abbreviated : bool, optional
            Whether or not the datetime string should use the abbreviated 
            format. The default is False.

        Returns
        -------
        result : string
            The locale formatted datetime string.

        """
        s = datetime_obj.strftime(self.datetime_format(abbreviated))
        return unicode(s)

    def from_int(self, value, base=10, group=False):
        """ Format the integer value according to the locale.

        Parameters
        ----------
        value : int
            The integer to convert a string.
        
        base : int, optional
            The number base to use when parsing the string. The valid
            values are the same as those passed to Python's builtin 
            'int'. The default is 10.

        group : bool, optional
            Whether or not to add group separators in the result. The
            default is False.
        
        Returns
        -------
        result : unicode string
            The locale formatted integer string.
        
        """
        # We can specially format bases 2, 8, 16. The others we format
        # as normal integers after converting them to a proper base.
        if base == 2:
            r = bin(value)
        elif base == 8:
            r = locale.format_string('%#o', value, group)
        elif base == 10:
            r = locale.format_string('%d', value, group)
        elif base == 16:
            r = locale.format_string('%#X', value, group)
        else:
            r = _convert_base(value, base)
        return unicode(r)

    def from_long(self, value, base=10, group=False):
        """ Format the long integer value according to the locale.

        Parameters
        ----------
        value : long
            The long integer to convert a string.
        
        base : int, optional
            The number base to use when parsing the string. The valid
            values are the same as those passed to Python's builtin 
            'int'. The default is 10.

        group : bool, optional
            Whether or not to add group separators in the result. The
            default is False.
        
        Returns
        -------
        result : unicode string
            The locale formatted long integer string.
        
        """
        # The int conversion can handle longs
        return self.from_int(value, base, group)

    def from_float(self, value, group=False, prec=-1):
        """ Format the float value according to the locale.

        Parameters
        ----------
        value : float
            The float to convert a string.
        
        group : bool, optional
            Whether or not to add group separators in the result. The
            default is False.
        
        prec : int, optional
            The number of signficant digits to display in the string. 
            The default is -1 which means the decision is left up
            to the implementor.

        Returns
        -------
        result : unicode string
            The locale formatted integer string.
        
        """
        if prec < 0:
            s = '%g'
        else:
            s = '%' + '.%dg' % prec
        return unicode(locale.format_string(s, value, group))

    def from_complex(self, value, group=False, prec=-1):
        """ Format the complex value according to the locale.

        Parameters
        ----------
        value : complex
            The complex to convert a string.
        
        group : bool, optional
            Whether or not to add group separators in the result. The
            default is False.
        
        prec : int, optional
            The number of signficant digits to display for each part. 
            The default is -1 which means the decision is left up
            to the implementor.

        Returns
        -------
        result : unicode string
            The locale formatted complex string.
        
        """
        real = self.from_float(value.real, group, prec)
        imag = self.from_float(value.imag, group, prec)
        if imag.startswith('-'):
            res = real + imag + 'j'
        else:
            res = real + '+' + imag + 'j'
        return res

    def from_currency(self, value, symbol=True, group=False, intl=False):
        """ Convert the given value into a locale specific currency
        string.

        Parameters
        ----------
        value : int, long, or float
            The value representing the currency
        
        symbol : bool, optional
            If True, the currency symbol is included in the string. The
            default is True.
        
        group : bool, optional
            If True, the grouping marks are included in the string. The
            default is False.
        
        intl : bool, optional
            If True, the international version of the currency symbol
            is used in the string. This is only used if 'symbol' is
            True. The default is False.
            
        Returns
        -------
        result : string
            The locale formatted currency string.
             
        """
        return unicode(locale.currency(value, symbol, group, intl))

