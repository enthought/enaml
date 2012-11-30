#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date as py_date

from dateutil.parser import parse as parse_iso_dt
from traits.api import Date, Property, on_trait_change

from enaml.core.trait_types import Bounded

from .control import Control


class BoundedDate(Control):
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
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(BoundedDate, self).snapshot()
        snap['minimum'] = self.minimum.isoformat()
        snap['maximum'] = self.maximum.isoformat()
        snap['date'] = self.date.isoformat()
        return snap

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
    def on_action_date_changed(self, content):
        """ Handle the 'date_changed' action from the UI control.

        """
        date = parse_iso_dt(content['date']).date()
        self.set_guarded(date=date)

    def _send_minimum(self):
        """ Send the minimum date to the client widget.

        """
        content = {'minimum': self.minimum.isoformat()}
        self.send_action('set_minimum', content)

    def _send_maximum(self):
        """ Send the maximum date to the client widget.

        """
        content = {'maximum': self.maximum.isoformat()}
        self.send_action('set_maximum', content)

    def _send_date(self):
        """ Send the current date to the client widget.

        """
        if 'date' not in self.loopback_guard:
            content = {'date': self.date.isoformat()}
            self.send_action('set_date', content)

    #--------------------------------------------------------------------------
    # Property methods
    #--------------------------------------------------------------------------
    def _get_minimum(self):
        """ The property getter for the minimum date.

        """
        return self._minimum

    def _set_minimum(self, date):
        """ The property setter for the minimum date.

        If the new minimum is greater than the current maximum, then the
        maximum will be adjusted up.

        """
        if date > self._maximum:
            self._maximum = date
        self._minimum = date

    def _get_maximum(self):
        """ The property getter for the maximum date.

        """
        return self._maximum

    def _set_maximum(self, date):
        """ The property setter for the maximum date.

        If the new maximum is less than the current minimum, then the
        minimum will be ajusted down.

        """
        if date < self._minimum:
            self._minimum = date
        self._maximum = date

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @on_trait_change('minimum, maximum')
    def _adapt_date(self):
        """ Actively adapt the date to lie within the boundaries.

        """
        self.date = min(max(self.date, self.minimum), self.maximum)

