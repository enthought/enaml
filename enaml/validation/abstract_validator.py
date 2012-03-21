#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from ..localization import get_default_locale
from ..localization.abstract_locale import AbstractLocale


class AbstractValidator(object):
    """ An abstract base class defining the behavior of validators.

    Validators are used to check the text input by the user is valid
    for conversion, perform that conversion when requested, and to
    format a user value to unicode string for display.

    """
    __metaclass__ = ABCMeta

    #: A constant representing a clearly invalid result. For example,
    #: the text 'asdf' is clearly invalid when a number string is
    #: expected.
    INVALID = 0

    #: A constant which represents a string which is in a plausible
    #: intermediate state on its way to being valid. For example the
    #: string '123' is intermediate if a 4 digit number string is 
    #: expected.
    INTERMEDIATE = 1

    #: A constant which represents a string that is acceptable inpute 
    #: for the current context.
    ACCEPTABLE = 2

    def __init__(self, locale=None):
        """ Initialize an AbstractValidator.

        Parameters
        ----------
        locale : AbstractLocale or None, optional
            If provided, a Locale object which may assist in converting
            to/from the string value. Whether or not the locale is used
            is dependent on the given subclass.

        """
        self.locale = locale
    
    def _get_locale(self):
        """ The property getter for the 'locale' attribute. This returns
        the current locale, or retrieves the default locale if one has 
        not yet been assigned to the validator.

        """
        locale = self._locale
        if locale is None:
            locale = self._locale = get_default_locale()
        return locale
    
    def _set_locale(self, value):
        """ The property setter for the 'locale' attribute.

        """
        if value is not None and not isinstance(value, AbstractLocale):
            msg = ('locale object must be an instance of AbstractLocale or '
                   'None. Got %s instead.')
            raise TypeError(msg % type(value))
        self._locale = value
    
    #: A property which returns the locale object for this validator.
    #: If one is not explicitly provided, the framework default locale
    #: object will be used.
    locale = property(_get_locale, _set_locale)

    @abstractmethod
    def validate(self, text):
        """ Validate the input text for the given context. 

        This is an abstract method and must be implemented by subclasses.
        This method should analyze the user text and return one of three
        class attribute constants: INVALID, INTERMEDIATE, or ACCEPTABLE. 
        These constants have the following semantic meanings:
            
            INVALID : The text is clearly invalid, and the addition of
                more characters cannot make it valid. Example: the text
                'asdf' is invalid when a number string is expected.

            INTERMEDIATE : The text is a plausible value that can be made
                valid with the addition of more text. Example: the text
                '123' is intermediate when a 4 digit number string is 
                expected.

            ACCEPTABLE : The text is an acceptable value. 

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.
        
        Returns
        -------
        result : int
            One of the class attribute constants INVALID, INTERMEDIATE, 
            or ACCEPTABLE.
        
        Notes
        -----
        This method will be called with high frequency. Implementations
        should therefore take care to make sure that the method executes
        quickly.

        """
        raise NotImplementedError
    
    @abstractmethod
    def convert(self, text):
        """ Convert the input text into an appropriate value.

        This is an abstract method and must be implemented by subclasses.
        This method is used to convert from the user input text into a
        context-dependent value. This method will only be called if the
        'validate' method returned an ACCEPTABLE result. When this method 
        is called is determined by the owner of the validator and is not
        necessarily immediately after a call to 'validate'.

        If the input text cannot be properly converted, a ValueError
        should be raised.

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.

        Returns
        -------
        result : object
            An appropriately converted object.

        """
        raise NotImplementedError

    @abstractmethod
    def format(self, value):
        """ Convert the input value into a string which is appropriate
        for display.

        This is an abstract method and must be implemented by subclasses.
        This method is used to convert from a context dependent model
        value into a unicode string suitable for display. This method
        will be called whenever a model value changes and the display
        should be updated. This method should always succeed.

        Parameters
        ----------
        value : object
            The context-dependent input value.

        Returns
        -------
        result : unicode string
            A formatted unicode string for display.

        """
        raise NotImplementedError

    def normalize(self, text):
        """ Attempt to convert the given input text into a valid unicode
        string according to the rules of the validator.

        This method may be called by various controls at various times,
        such as when the control loses focus. This provides a chance for
        the programmer to coerce the text into a valid string or to fix
        the formatting of the user string. It is not necessary to return
        a valid value from this method, as the returned value will be 
        tested again for validity. The default implementation of this 
        method does nothing and returns the input string.

        If the method cannot properly normalize the string, the original
        text should be returned.

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.

        Returns
        -------
        result : unicode string
            The string to use in the control in lieu of the user supplied
            string.
        
        """
        return text

