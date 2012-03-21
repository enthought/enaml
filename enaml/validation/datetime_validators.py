#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .coercing_validator import CoercingValidator


class BaseDTValidator(CoercingValidator):
    """ A CoercingValidator subclass which provides common functionality
    for the time, date, and datetime validators.

    """
    def __init__(self, abbreviated=True, **kwargs):
        """ Initialize a BaseDTValidator.

        Parameters
        ----------
        abbreviated : bool, optional
            Whether or not to use abbreviated time formatting. Defaults
            to True.
        
        **kwargs
            The keyword arguments necessary to initialize an instance
            of CoercingValidator.

        """
        super(BaseDTValidator, self).__init__(**kwargs)
        self.abbreviated = abbreviated

    def validate(self, text):
        """ Validates the input text against the rules of the validator.

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.
        
        Returns
        -------
        result : int
            One of the class attribute constants INVALID, INTERMEDIATE, 
            or VALID.
        
        Notes
        -----
        The string is INVALID under the following conditions:
            - The string fails coercing validation.
        
        The string is INTERMEDIATE under the following conditions:
            - The string is empty.

        The string is VALID for all other situations.

        """
        if not text:
            return self.INTERMEDIATE
        return self._validate(text)[0]


class TimeValidator(BaseDTValidator):
    """ A BaseDTValidator subclass which uses the locale information to 
    convert to and from datetime.time objects.

    """
    def _convert(self, text):
        """ Overridden default convert method which uses the locale 
        object to convert the text into a datetime.time object.

        """
        return self.locale.to_time(text, abbreviated=self.abbreviated)

    def _format(self, value):
        """ Overridden default convert method which uses the locale 
        object to format the datetime.time object into a string.

        """
        return self.locale.from_time(value, abbreviated=self.abbreviated)


class DateValidator(BaseDTValidator):
    """ A BaseDTValidator subclass which uses the locale information to 
    convert to and from datetime.date objects.

    """
    def _convert(self, text):
        """ Overridden default convert method which uses the locale 
        object to convert the text into a datetime.date object.

        """
        return self.locale.to_date(text, abbreviated=self.abbreviated)

    def _format(self, value):
        """ Overridden default convert method which uses the locale 
        object to format the datetime.time object into a string.

        """
        return self.locale.from_date(value, abbreviated=self.abbreviated)


class DatetimeValidator(BaseDTValidator):
    """ A BaseDTValidator subclass which uses the locale information to 
    convert to and from datetime.datetime objects.

    """
    def _convert(self, text):
        """ Overridden default convert method which uses the locale 
        object to convert the text into a datetime.datetime object.

        """
        return self.locale.to_datetime(text, abbreviated=self.abbreviated)

    def _format(self, value):
        """ Overridden default convert method which uses the locale 
        object to format the datetime.time object into a string.

        """
        return self.locale.from_datetime(value, abbreviated=self.abbreviated)

