#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date as py_date

from dateutil.parser import parse as parse_iso_dt
from traits.api import Date, Property, TraitError, on_trait_change

from enaml.core.trait_types import Bounded

from .constraints_widget import ConstraintsWidget


class BoundedDate(ConstraintsWidget):
    """ A base class for components which edit a Python datetime.date 
    object bounded between minimum and maximum values. 

    This class is not meant to be used directly.

    """
    #: The minimum date available in the date edit. If not defined then
    #: the default value is September 14, 1752.
    minimum = Property(Date, depends_on ='_minimum')

    #: The internal minimum date storage
    _minimum = Date(py_date(1752, 9, 14))

    #: The maximum date available in the date edit. If not defined then
    #: the default value is December 31, 7999.
    maximum = Property(Date, depends_on ='_maximum')

    #: The internal maximum date storage
    _maximum = Date(py_date(7999, 12, 31))

    #: The currently selected date. Default is the current date. The
    #: value is bounded between :attr:`minimum` and :attr:`maximum`. 
    date = Bounded(Date(py_date.today()), low='minimum', high='maximum')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(BoundedDate, self).creation_attributes()
        super_attrs['minimum'] = self.minimum.isoformat()
        super_attrs['maximum'] = self.maximum.isoformat()
        super_attrs['date'] = self.date.isoformat()
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(BoundedDate, self).bind()
        otc = self.on_trait_change
        otc(self._send_minimum, 'minimum')
        otc(self._send_maximum, 'maximum')
        otc(self._send_date, 'date')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_changed(self, payload):
        """ Handle the 'event-changed' message from the UI control.

        """
        date = parse_iso_dt(payload['date']).date()
        self.set_guarded(date=date)

    def _send_minimum(self):
        """ Send the minimum date to the client widget.

        """
        payload = {
            'action': 'set-minimum', 'minimum': self.minimum.isoformat(),
        }
        self.send_message(payload)

    def _send_maximum(self):
        """ Send the maximum date to the client widget.

        """
        payload = {
            'action': 'set-maximum', 'maximum': self.maximum.isoformat(),
        }
        self.send_message(payload)

    def _send_date(self):
        """ Send the current date to the client widget.

        """
        if 'date' not in self.loopback_guard:
            payload = {'action': 'set-date', 'date': self.date.isoformat()}
            self.send_message(payload)

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
    
    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @on_trait_change('minimum, maximum')
    def _adapt_date(self):
        """ Actively adapt the date to lie within the boundaries.

        """
        if self.initialized:
            self.date = min(max(self.date, self.minimum), self.maximum)

