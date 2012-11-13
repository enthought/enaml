#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime, time

from dateutil.parser import parse as parse_iso_dt
from traits.api import Property, Time, on_trait_change

from enaml.core.trait_types import Bounded

from .control import Control


class BoundedTime(Control):
    """ A base class for use with widgets that edit a Python
    datetime.time object bounded between minimum and maximum
    values. This class is not meant to be used directly.

    """
    #: The minimum time available in the control. If not defined then
    #: the default value is midnight.
    minimum = Property(Time, depends_on ='_minimum')

    #: The internal minimum time storage.
    _minimum = Time(time(0, 0, 0, 0))

    #: The maximum time available in the control. If not defined then
    #: the default value is the second before midnight.
    maximum = Property(Time, depends_on ='_maximum')

    #: The internal maximum time storage.
    _maximum = Time(time(23, 59, 59, 999000))

    #: The currently selected time. Default is datetime.now().time(). The
    #: value is bounded between :attr:`minimum` and :attr:`maximum`.
    time = Bounded(Time(datetime.now().time()), low='minimum', high='maximum')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(BoundedTime, self).snapshot()
        snap['minimum'] = self.minimum.isoformat()
        snap['maximum'] = self.maximum.isoformat()
        snap['time'] = self.time.isoformat()
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(BoundedTime, self).bind()
        otc = self.on_trait_change
        otc(self._send_minimum, 'minimum')
        otc(self._send_maximum, 'maximum')
        otc(self._send_time, 'time')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_time_changed(self, content):
        """ The handler for the 'time_changed' action sent from the
        client widget.

        """
        time = parse_iso_dt(content['time']).time()
        self.set_guarded(time=time)

    def _send_minimum(self):
        """ Send the minimum time to the client widget.

        """
        content = {'minimum': self.minimum.isoformat()}
        self.send_action('set_minimum', content)

    def _send_maximum(self):
        """ Send the maximum time to the client widget.

        """
        content = {'maximum': self.maximum.isoformat()}
        self.send_action('set_maximum', content)

    def _send_time(self):
        """ Send the current time to the client widget.

        """
        if 'time' not in self.loopback_guard:
            content = {'time': self.time.isoformat()}
            self.send_action('set_time', content)

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    def _get_minimum(self):
        """ The property getter for the minimum time.

        """
        return self._minimum

    def _set_minimum(self, time):
        """ The property setter for the minimum time.

        If the new minimum is greater than the current maximum, then the
        maximum will be adjusted up.

        """
        if time > self._maximum:
            self._maximum = time
        self._minimum = time

    def _get_maximum(self):
        """ The property getter for the maximum time.

        """
        return self._maximum

    def _set_maximum(self, time):
        """ The property setter for the maximum time.

        If the new maximum is less than the current minimum, then the
        minimum will be ajusted down.

        """
        if time < self._minimum:
            self._minimum = time
        self._maximum = time

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @on_trait_change('minimum, maximum')
    def _adapt_time(self):
        """ Actively adapt the time to lie within the boundaries.

        """
        self.time = min(max(self.time, self.minimum), self.maximum)

