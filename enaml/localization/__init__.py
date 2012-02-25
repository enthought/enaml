#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .abstract_locale import AbstractLocale
from .system_locale import SystemLocale


#: The storage for the framework default locale object
_default_locale = None


def set_default_locale(locale_obj):
    """ Sets the framework-wide default locale.

    Parameters
    ----------
    locale_obj : AbstractLocale
        An instance of AbstractLocale which will be used as the default
        locale for the Enaml framework.

    """
    global _default_locale
    if locale_obj is not None and not isinstance(locale_obj, AbstractLocale):
        msg = ('Locale object must be an instance of AbstractLocale or None. '
               'Got %s instead.' % type(locale_obj))
        raise TypeError(msg)
    _default_locale = locale_obj


def get_default_locale():
    """ Returns the framework-wide default locale object. If a default
    has not been explicitly provided, this will return the default
    SystemLocale

    """
    locale_obj = _default_locale
    if locale_obj is None:
        locale_obj = SystemLocale.default()
        set_default_locale(locale_obj)
    return locale_obj

