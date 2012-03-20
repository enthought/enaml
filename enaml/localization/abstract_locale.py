#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractLocale(object):
    """ An abstract base class defining the required api for a locale 
    object to be used by the framework.

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
        """ The monetary negative sign for the locale.

        """
        raise NotImplementedError
        
    @abstractproperty
    def positive_sign(self):
        """ The monetary positive sign for the locale.

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
        result : unicode string
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
        result : unicode string
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
        result : unicode string
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
        result : unicode string
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
        result : unicode string
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
        result : unicode string
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
        result : unicode string
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
        result : unicode string
            The locale formatted datetime string.

        """
        raise NotImplementedError
    
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
            The locale formatted float string.
        
        """
        raise NotImplementedError

    @abstractmethod
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
        result : unicode string
            The locale formatted currency string.

        """
        raise NotImplementedError

