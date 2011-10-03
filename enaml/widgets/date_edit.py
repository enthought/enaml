#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

from traits.api import Date, Event, Instance, Str

from .control import Control, IControlImpl


class IDateEditImpl(IControlImpl):

    def parent_date_changed(self, date):
        raise NotImplementedError

    def parent_minimum_date_changed(self, date):
        raise NotImplementedError

    def parent_maximum_date_changed(self, date):
        raise NotImplementedError


class DateEdit(Control):
    """ A date widget.

    A DateEdit displays a Python datetime.date using an appropriate
    toolkit specific control. This is a smaller control than what is
    provided by Calendar.

    Attributes
    ----------
    date : Date
        The currently selected date. Default is the current date.

    minimum_date : Date
        The minimum date available in the date edit. If not defined then
        the default value is September 14, 1752

    maximum_date : Date
        The maximum date available in the date edit. If not defined then
        the default value is December 31, 7999

    format : Str
        A python date format string to format the date. If none is
        supplied (or is invalid) the system locale setting is used.
        This may not be supported by all backends.

    activated : Event
        Triggered whenever the user clicks or changes the control. The
        event payload will be the date on the control.

    """
    date = Date(datetime.date.today())

    minimum_date = Date(datetime.date(1752, 9, 14))

    maximum_date = Date(datetime.date(7999, 12, 31))

    format = Str

    activated = Event

    #---------------------------------------------------------------------------
    # Overridden parent traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IDateEditImpl)


DateEdit.protect('activated')

