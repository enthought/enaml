#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date

from traits.api import Date, Property, TraitError, on_trait_change

from enaml.core.trait_types import Bounded

from .constraints_widget import ConstraintsWidget


#: The attributes of a BoundedDate to proxy to clients.
_DATE_ATTRS = ['minimum', 'maximum', 'date']


class BoundedDate(ConstraintsWidget):
    """ A base class for components which edit a Python datetime.date 
    object bounded between minimum and maximum values. 

    This class is not meant to be used directly.

    """
    #: The minimum date available in the date edit. If not defined then
    #: the default value is September 14, 1752.
    minimum = Property(Date, depends_on ='_minimum')

    #: The internal minimum date storage
    _minimum = Date(date(1752, 9, 14))

    #: The maximum date available in the date edit. If not defined then
    #: the default value is December 31, 7999.
    maximum = Property(Date, depends_on ='_maximum')

    #: The internal maximum date storage
    _maximum = Date(date(7999, 12, 31))

    #: The currently selected date. Default is the current date. The
    #: value is bounded between :attr:`minimum` and :attr:`maximum`. 
    date = Bounded(Date(date.today()), low='minimum', high='maximum')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(BoundedDate, self).creation_attributes()
        attrs = dict((attr, getattr(self, attr)) for attr in _DATE_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(BoundedDate, self).bind()
        self.publish_attributes(*_DATE_ATTRS)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_set_date(self, payload):
        """ Handle the 'set-date' message from the UI control.

        """
        pass

    #--------------------------------------------------------------------------
    # Property methods
    #--------------------------------------------------------------------------
    def _get_minimum(self):
        """ The property getter for the minimum date.

        """
        return self._minimum

    def _set_minimum(self, date):
        """ Set the minimum date. Addtional checks are applied to make 
        sure that :attr:`minimum` < :attr:`maximum`

        """
        if date > self.maximum:
            msg = ("The minimum date should be smaller than the current "
                   "maximum date({0}), but a value of {1} was given.")
            msg = msg.format(self.maximum, date)
            raise TraitError(msg)
        self._minimum = date

    def _get_maximum(self):
        """ The property getter for the maximum date.

        """
        return self._maximum

    def _set_maximum(self, date):
        """ Set the maximum date. Addtional checks are applied to make 
        sure that :attr:`minimum` < :attr:`maximum`

        """
        if date < self.minimum:
            msg = ("The maximum date should be larger than the current "
                   "minimum date({0}), but a value of {1} was given.")
            msg = msg.format(self.minimum, date)
            raise TraitError(msg)
        self._maximum = date
    
    @on_trait_change('minimum, maximum')
    def _adapt_date(self):
        """ Actively adapt the date to lie within the boundaries.

        """
        if self.initialized:
            self.date = min(max(self.date, self.minimum), self.maximum)

