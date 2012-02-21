#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
import datetime
import locale
import time


#------------------------------------------------------------------------------
# Abstract Locale
#------------------------------------------------------------------------------
class AbstractLocale(object):
    """ An abstract base class defining the required api for a locale 
    object to be used by the framework. Enaml provides a default locale
    implementation in the form of SystemLocale.

    """
    __metaclass__ = ABCMeta

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @abstractproperty
    def name(self):
        """ The RFC 1766 language code for the locale.

        """
        raise NotImplementedError

    @abstractproperty
    def encoding(self):
        """ The encoding for strings in the locale.

        """
        raise NotImplementedError
        
    @abstractproperty
    def am_string(self):
        """ The string for "AM" time in the locale.

        """
        raise NotImplementedError
    
    @abstractproperty
    def pm_string(self):
        """ The string for "PM" time in the locale.

        """
        raise NotImplementedError

    @abstractproperty
    def decimal_point(self):
        """ The decimal separator for the locale.

        """
        raise NotImplementedError
    
    @abstractproperty
    def monetary_decimal_point(self):
        """ The decimal separator for monetary values for the locale.

        """
        raise NotImplementedError

    @abstractproperty
    def exponential(self):
        """ The exponential character for the locale.

        """
        raise NotImplementedError

    @abstractproperty
    def thousands_separator(self):
        """ The thousands separator for the locale.

        """
        raise NotImplementedError
    
    @abstractproperty
    def monetary_thousands_separator(self):
        """ The thousands separator for monetary values for the locale.

        """
        raise NotImplementedError

    @abstractproperty
    def negative_sign(self):
        """ The negative sign for the locale.

        """
        raise NotImplementedError
        
    @abstractproperty
    def positive_sign(self):
        """ The positive sign for the locale.

        """
        raise NotImplementedError
    
    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------
    @abstractmethod
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
        raise NotImplementedError
    
    @abstractmethod
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
        raise NotImplementedError
        
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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

        """
        raise NotImplementedError
    
    @abstractmethod
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

        """
        raise NotImplementedError
    
    #--------------------------------------------------------------------------
    # Conversions
    #--------------------------------------------------------------------------
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
    
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
    
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        result : string
            The locale formatted time string.

        """
        raise NotImplementedError
    
    @abstractmethod
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
        result : string
            The locale formatted date string.

        """
        raise NotImplementedError
    
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    
#------------------------------------------------------------------------------
# System Locale
#------------------------------------------------------------------------------
class SystemLocale(object):
    """ An AbstractLocale implementation which uses the Python 'locale'
    module for locale information. 

    The SystemLocale does not maintain any state and will always reflect 
    the current system locale information as given by the 'locale' module.

    """
    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def name(self):
        """ The RFC 1766 language code for the locale.

        """
        return locale.getlocale()[0]

    @property
    def encoding(self):
        """ The encoding for strings in the locale.

        """
        return locale.getlocale()[1]
                
    @property
    def am_string(self):
        """ The string for "AM" time in the locale.

        """
        return locale.nl_langinfo(locale.AM_STR)
    
    @property
    def pm_string(self):
        """ The string for "PM" time in the locale.

        """
        return locale.nl_langinfo(locale.PM_STR)

    @property
    def decimal_point(self):
        """ The decimal separator for the locale.

        """
        return locale.localeconv()['decimal_point']
            
    @property
    def monetary_decimal_point(self):
        """ The decimal separator for monetary values for the locale.

        """
        return locale.localeconv()['mon_decimal_point']

    @property
    def exponential(self):
        """ The exponential character for the locale.

        """
        # Symbol not provided by locale module, so use Python default
        return 'e'

    @property
    def thousands_separator(self):
        """ The thousands separator for the locale.

        """
        return locale.localeconv()['thousands_sep']
    
    @property
    def monetary_thousands_separator(self):
        """ The thousands separator for monetary values for the locale.

        """
        return locale.localeconv()['mon_thousands_sep']

    @property
    def negative_sign(self):
        """ The negative sign for the locale.

        """
        return locale.localeconv()['negative_sign']
                
    @property
    def positive_sign(self):
        """ The positive sign for the locale.

        """
        return locale.localeconv()['positive_sign']
            
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
        prefix = 'AB' if abbreviated else ''
        attr = prefix + ('MON_%i' % month_int)
        flag = getattr(locale, attr)
        return locale.nl_langinfo(flag)

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
        prefix = 'AB' if abbreviated else ''
        attr = prefix + ('DAY_%i' % day_int)
        flag = getattr(locale, attr)
        return locale.nl_langinfo(flag)
        
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
        flag = locale.T_FMT if abbreviated else locale.T_FMT_AMPM
        return locale.nl_langinfo(flag)

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
        # Python doesn't support %e in strptime, but %d is equivalent
        return locale.nl_langinfo(locale.D_FMT).replace('%e', '%d')

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
        # Python doesn't support %e in strptime, but %d is equivalent
        return locale.nl_langinfo(locale.D_T_FMT).replace('%e', '%d')
        
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
        result : string
            The locale formatted time string.

        """
        return time_obj.strftime(self.time_format(abbreviated))
    
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
        result : string
            The locale formatted date string.

        """
        return date_obj.strftime(self.date_format(abbreviated))
    
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
        return datetime_obj.strftime(self.datetime_format(abbreviated))

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
        return locale.currency(value, symbol, group, intl)

