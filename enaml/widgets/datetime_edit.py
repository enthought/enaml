#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime as python_datetime

from traits.api import Event, Instance, Str

from .control import Control, IControlImpl


class IDatetimeEditImpl(IControlImpl):

    def parent_datetime_changed(self, datetime):
        raise NotImplementedError

    def parent_minimum_datetime_changed(self, datetime):
        raise NotImplementedError

    def parent_maximum_datetime_changed(self, datetime):
        raise NotImplementedError

    def parent_format_changed(self, datetime):
        raise NotImplementedError


class DatetimeEdit(Control):
    """ A datetime widget.

    A DatetimeEdit displays a Python datetime.datetime using an
    appropriate toolkit specific control. The component behaves like the
    Qt DateTimeEdit widget.

    Attributes
    ----------
    datetime : Instance(datetime.datetime)
        The currently selected datetime. Default value is the current
        time in the machine. The value is bounded between
        :attr:`minimum_datetime` and :attr:`maximum_date`. Attempts to
        assign a value outside of this range will result in a TraitError.

    minimum_datetime : Instance(datetime.datetime)
        The minimum datetime available in the date edit. By default, this
        property contains a date that refers to September 14, 1752 and a
        time of 00:00:00 and 0 milliseconds.

    maximum_datetime : Instance(datetime.datetime)
        The maximum datetime available in the date edit. By default, this
        property contains a date that refers to 31 December, 7999 and a
        time of 23:59:59 and 999 milliseconds.

    format : Str
        A python date format string to format the datetime. If none is
        supplied (or is invalid) the system locale setting is used.
        This may not be supported by all backends.

    datetime_changed : Event
        Triggered whenever the user clicks or changes the control. The
        event payload will be the datetime on the control.

    """
    datetime = Instance(python_datetime, factory=python_datetime.now)

    minimum_datetime = Instance(python_datetime,
                                args=(1752,9,14, 0, 0, 0, 0))

    maximum_datetime = Instance(python_datetime,
                                args=(7999, 12, 31, 23, 59, 59, 999000))

    format = Str

    datetime_changed = Event

    #---------------------------------------------------------------------------
    # Overridden parent traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IDatetimeEditImpl)


DatetimeEdit.protect('datetime_changed')

