#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime as py_datetime

from traits.api import Property, BaseInstance, TraitError, on_trait_change

from enaml.core.trait_types import Bounded

from .constraints_widget import ConstraintsWidget


#: The attributes of a BoundedDatetim to proxy to clients.
_DT_PROXY_ATTRS = ['minimum', 'maximum', 'value']


#: A custom trait which validates Python datetime instances.
Datetime = BaseInstance(py_datetime)


class BoundedDatetime(ConstraintsWidget):
    """ A base class for use with widgets that edit a Python 
    datetime.datetime object bounded between minimum and maximum 
    values. This class is not meant to be used directly.

    """
    #: The minimum datetime available in the datetime edit. If not 
    #: defined then the default value is midnight September 14, 1752.
    minimum = Property(Datetime, depends_on ='_minimum')

    #: The internal minimum datetime storage
    _minimum = Datetime(py_datetime(1752, 9, 14, 0, 0, 0, 0))

    #: The maximum datetime available in the datetime edit. If not 
    #: defined then the default value is the second before midnight
    #: December 31, 7999.
    maximum = Property(Datetime, depends_on ='_maximum')

    #: The internal maximum datetime storage
    _maximum = Datetime(py_datetime(7999, 12, 31, 23, 59, 59, 999000))

    #: The currently selected date. Default is datetime.now(). The
    #: value is bounded between :attr:`minimum` and :attr:`maximum`. 
    value = Bounded(Datetime(py_datetime.now()), low='minimum', high='maximum')
                    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(BoundedDatetime, self).bind()
        self.default_send(*_DT_PROXY_ATTRS)

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(BoundedDatetime, self).initial_attrs()
        attrs = dict((attr, getattr(self, attr)) for attr in _DT_PROXY_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Properties methods
    #--------------------------------------------------------------------------
    def _get_minimum(self):
        """ The property getter for the minimum datetime.

        """
        return self._minimum

    def _set_minimum(self, datetime):
        """ Set the minimum datetime. Addtional checks are perfomed to 
        make sure that :attr:`minimum` < :attr:`maximum`

        """
        if datetime > self.maximum:
            msg = ("The minimum datetime of DatetimeEdit should be smaller "
                   "than the current maximum datetime({0}), but a value of "
                   "{1} was given ")
            msg = msg.format(self.maximum, datetime)
            raise TraitError(msg)
        self._minimum = datetime

    def _get_maximum(self):
        """ The property getter for the maximum datetime.

        """
        return self._maximum

    def _set_maximum(self, datetime):
        """ Set the maximum datetime. Addtional checks are perfomed to 
        make sure that :attr:`minimum` < :attr:`maximum`

        """
        if datetime < self.minimum:
            msg = ("The maximum datetime of DatetimeEdit should be larger "
                   "than the current minimum datetime({0}), but a value of "
                   "{1} was given ")
            msg = msg.format(self.minimum, datetime)
            raise TraitError(msg)
        self._maximum = datetime

    @on_trait_change('minimum, maximum')
    def _adapt_value(self):
        """ Actively adapt the datetime to lie within the boundaries.

        """
        if self.initialized:
            self.value = min(max(self.value, self.minimum), self.maximum)

