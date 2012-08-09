#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime as py_datetime

from dateutil.parser import parse as parse_iso_dt
from traits.api import Property, BaseInstance, TraitError, on_trait_change

from enaml.core.trait_types import Bounded

from .constraints_widget import ConstraintsWidget


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
    datetime = Bounded(Datetime(py_datetime.now()), low='minimum', high='maximum')
                    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(BoundedDatetime, self).snapshot()
        snap['minimum'] = self.minimum.isoformat()
        snap['maximum'] = self.maximum.isoformat()
        snap['datetime'] = self.datetime.isoformat()
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(BoundedDatetime, self).bind()
        otc = self.on_trait_change
        otc(self._send_minimum, 'minimum')
        otc(self._send_maximum, 'maximum')
        otc(self._send_datetime, 'datetime')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_datetime_changed(self, content):
        """ The handler for the 'datetime_changed' aciton sent from the
        client widget.

        """
        datetime = parse_iso_dt(content['datetime'])
        self.set_guarded(datetime=datetime)
        
    def _send_minimum(self):
        """ Send the minimum datetime to the client widget.

        """
        content = {'minimum': self.minimum.isoformat()}
        self.send_action('set_minimum', content)

    def _send_maximum(self):
        """ Send the maximum datetime to the client widget.

        """
        content = {'maximum': self.maximum.isoformat()}
        self.send_action('set_maximum', content)

    def _send_datetime(self):
        """ Send the current datetime to the client widget.

        """
        if 'datetime' not in self.loopback_guard:
            content = {'datetime': self.datetime.isoformat()}
            self.send_action('set_datetime', content)

    #--------------------------------------------------------------------------
    # Properties
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

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @on_trait_change('minimum, maximum')
    def _adapt_datetime(self):
        """ Actively adapt the datetime to lie within the boundaries.

        """
        if self.initialized:
            self.datetime = min(max(self.datetime, self.minimum), self.maximum)

