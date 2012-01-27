#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod
from datetime import datetime as py_datetime

from traits.api import (
    Property, BaseInstance, Instance, TraitError, on_trait_change,
)

from .control import Control, AbstractTkControl

from ..core.trait_types import Bounded


Datetime = BaseInstance(py_datetime)


class AbstractTkBoundedDatetime(AbstractTkControl):

    @abstractmethod
    def shell_datetime_changed(self, datetime):
        raise NotImplementedError

    @abstractmethod
    def shell_min_datetime_changed(self, datetime):
        raise NotImplementedError

    @abstractmethod
    def shell_max_datetime_changed(self, datetime):
        raise NotImplementedError


class BoundedDatetime(Control):
    """ A base class for use with widgets that edit a Python 
    datetime.datetime object bounded between minimum and maximum 
    values. This class is not meant to be used directly.

    """
    #: The currently selected datetime. Default value is the current
    #: date and time in the machine. The value is bounded between
    #: :attr:`min_datetime` and :attr:`max_datetime`. Changing the
    #: boundary attributes might result in an update of :attr:`datetime` 
    #: to fit in the new range. Attempts to assign a value outside of 
    #: these bounds will result in a TraitError.
    datetime = Bounded(Datetime(py_datetime.now()),
                       low='min_datetime', high='max_datetime')
                    
    #: The minimum datetime available in the date edit. By default, this
    #: property contains a date that refers to September 14, 1752 and a
    #: time of 00:00:00 and 0 milliseconds. Extra checks take place to
    #: make sure that the user does not programmatically set
    #: :attr:`min_datetime` > :attr:`max_datetime`.
    min_datetime = Property(Datetime, depends_on='_min_datetime')

    #: The internal min datetime storage
    _min_datetime = Datetime(py_datetime(1752,9,14, 0, 0, 0, 0))

    #: The maximum datetime available in the date edit. By default, this
    #: property contains a date that refers to 31 December, 7999 and a
    #: time of 23:59:59 and 999 milliseconds. Extra checks take place to
    #: make sure that the user does not programmatically set
    #: :attr:`min_datetime` > :attr:`max_datetime`.
    max_datetime = Property(Datetime, depends_on='_max_datetime')

    #: The internal max datetime storage
    _max_datetime = Datetime(py_datetime(7999, 12, 31, 23, 59, 59, 999000))

    #: Overridden parent trait
    abstract_obj = Instance(AbstractTkBoundedDatetime)

    #--------------------------------------------------------------------------
    # Properties methods
    #--------------------------------------------------------------------------
    def _set_min_datetime(self, datetime):
        """ Set the min_datetime.

        Addtional checks are perfomed to make sure that
        :attr:`min_datetime` < :attr:`max_datetime`

        """
        if datetime > self.max_datetime:
            msg = ("The minimum datetime of DatetimeEdit should be smaller "
                    "than the current maximum datetime({0}), but a value of "
                    "{1} was given ")
            msg = msg.format(self.max_datetime, datetime)
            raise TraitError(msg)
        self._min_datetime = datetime

    def _set_max_datetime(self, datetime):
        """ Set the max_datetime.

        Addtional checks are perfomed to make sure that
        :attr:`minimum_datetime` < :attr:`maximum_datetime`

        """
        if datetime < self.min_datetime:
            msg = ("The maximum datetime of DatetimeEdit should be larger "
                   "than the current minimum datetime({0}), but a value of "
                   "{1} was given ")
            msg = msg.format(self.min_datetime, datetime)
            raise TraitError(msg)
        self._max_datetime = datetime

    def _get_max_datetime(self):
        """ The property getter for the max datetime.

        """
        return self._max_datetime

    def _get_min_datetime(self):
        """ The property getter for the min datetime.

        """
        return self._min_datetime

    @on_trait_change('min_datetime, max_datetime')
    def _adapt_datetime(self):
        """ Adapt the date to the bounderies

        """
        if self.initialized:
            min_dt, max_dt = self.min_datetime, self.max_datetime
            self.datetime = min(max(self.datetime, min_dt), max_dt)

