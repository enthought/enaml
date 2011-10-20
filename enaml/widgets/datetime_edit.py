#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime as python_datetime

from traits.api import Event, Str, Property, BaseInstance, Instance, TraitError

from .control import Control, IControlImpl
from ..util.trait_types import Bounded


Datetime = BaseInstance(python_datetime)

class IDatetimeEditImpl(IControlImpl):

    def parent_datetime_changed(self, datetime):
        raise NotImplementedError

    def parent__minimum_datetime_changed(self, datetime):
        raise NotImplementedError

    def parent__maximum_datetime_changed(self, datetime):
        raise NotImplementedError

    def parent_datetime_format_changed(self, datetime_format):
        raise NotImplementedError


class DatetimeEdit(Control):
    """ A datetime widget.

    A DatetimeEdit displays a Python datetime.datetime using an
    appropriate toolkit specific control. The component behaves like the
    Qt DateTimeEdit widget, so the accurancy is in milliseconds.

    Attributes
    ----------
    datetime : Bounded(trait=Datetime)
        The currently selected datetime. Default value is the current
        date and time in the machine. The value is bounded between
        :attr:`minimum_datetime` and :attr:`maximum_date`. Changing the
        boundary attributes might result in an update of :attr:`date` to fit
        in the new range. Attempts to assign a value outside of these bounds
        will result in a TraitError.

    minimum_datetime : Property(Datetime)
        The minimum datetime available in the date edit. By default, this
        property contains a date that refers to September 14, 1752 and a
        time of 00:00:00 and 0 milliseconds. Extra checks take place to
        make sure that the user does not programmatically set
        :attr:`minimum_datetime` > :attr:`maximum_datetime`.

    maximum_datetime : Property(Datetime)
        The maximum datetime available in the date edit. By default, this
        property contains a date that refers to 31 December, 7999 and a
        time of 23:59:59 and 999 milliseconds. Extra checks take place to
        make sure that the user does not programmatically set
        :attr:`minimum_datetime` > :attr:`maximum_datetime`.

    datetime_format : Str
        A python date format string to format the datetime. If None is
        supplied (or is invalid) the system locale setting is used.
        This may not be supported by all backends.

    datetime_changed : Event
        Triggered whenever the user clicks or changes the control. The
        event payload will be the datetime on the control.

    """
    datetime = Bounded(Datetime(python_datetime.now()), low='minimum_datetime',
                        high='maximum_datetime')

    minimum_datetime = Property(Datetime, depends_on='_minimum_datetime')
    _minimum_datetime = Datetime(python_datetime(1752,9,14, 0, 0, 0, 0))

    maximum_datetime = Property(Datetime, depends_on='_maximum_datetime')
    _maximum_datetime = Datetime(python_datetime(7999, 12, 31, 23, 59, 59, 999000))

    datetime_format = Str

    datetime_changed = Event

    #---------------------------------------------------------------------------
    # Overridden parent traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IDatetimeEditImpl)

    #---------------------------------------------------------------------------
    # Properties
    #---------------------------------------------------------------------------
    def _set_minimum_datetime(self, datetime):
        """ Set the minimum_datetime.

        Addtional checks are perfomed to make sure that
        :attr:`minimum_datetime` < :attr:`maximum_datetime`

        """
        if datetime > self._maximum_datetime:
            msg = ("The minimum datetime of DatetimeEdit should be smaller than "
                    "the current maximum datetime({0}), but a value of {1} was "
                    "given ".format(self._maximum_date, datetime))
            raise TraitError(msg)
        self._minimum_datetime = datetime
        self._adapt_datetime()

    def _set_maximum_datetime(self, datetime):
        """ Set the maximum_date.

        Addtional checks are perfomed to make sure that
        :attr:`minimum_datetime` < :attr:`maximum_datetime`

        """
        if datetime < self._minimum_datetime:
            msg = ("The maximum datetime of DatetimeEdit should be larger than "
                    "the current minimum datetime({0}), but a value of {1} was "
                    "given ".format(self._minimum_datetime, datetime))
            raise TraitError(msg)
        self._maximum_datetime = datetime
        self._adapt_datetime()

    def _get_maximum_datetime(self):
        """ The property getter for the slider maximum.

        """
        return self._maximum_datetime

    def _get_minimum_datetime(self):
        """ The property getter for the slider minimum.

        """
        return self._minimum_datetime

    # FIXME: I would like to have this method use the on_change decorator, but
    # it should not be run while the component is initialized so that an
    # exception is raised when the enaml source contains invalid values.
    def _adapt_datetime(self):
        """ Adapt the date to the bounderies

        """
        datetime = self.datetime
        datetime = max(datetime, self._minimum_datetime)
        datetime = min(datetime, self._maximum_datetime)
        self.datetime = datetime


DatetimeEdit.protect('datetime_changed', 'minimum_datetime','_minimum_datetime',
                     'maximum_datetime','_maximum_datetime')
