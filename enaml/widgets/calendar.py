#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date

from traits.api import Date, Event, Instance

from .control import Control, IControlImpl


class ICalendarImpl(IControlImpl):

    def parent_date_changed(self, obj, name, old_date, new_date):
        raise NotImplementedError
    
    def parent_minimum_date_changed(self, date):
        raise NotImplementedError
    
    def parent_maximum_date_changed(self, date):
        raise NotImplementedError


class Calendar(Control):
    """ A calendar widget.

    A Calendar displays a Python datetime.date using an appropriate
    toolkit specific control.
    
    Attributes
    ----------
    date : Date
        The currently selected date. This is only updated when the user
        *activates* the control via double-click or pressing enter.

    minimum_date : Date
        The minimum date available in the calendar.

    maximum_date : Date
        The maximum date available in the calendar.
    
    selected : Event
        Triggered whenever the user clicks or changes the control. The
        event payload will be the date on the control.
    
    activated : Event
        Triggered whenever the user activates a new date via double
        click or pressing enter. The event payload will be the date
        on the control.

    """    
    date = Date(date.today())

    minimum_date = Date

    maximum_date = Date

    selected = Event

    activated = Event

    #---------------------------------------------------------------------------
    # Overridden parent traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ICalendarImpl)


Calendar.protect('selected', 'activated')

