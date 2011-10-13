#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

from traits.api import Date, Event, Instance

from .control import Control, IControlImpl
from ..util.trait_types import Bounded

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
    date : Bounded
        The currently selected date. This is only updated when the user
        *activates* the control via double-click or pressing enter. The
        value is bounded between :attr:`minimum_date` and
        :attr:`maximum_date`. Attempts to assign a value outside of this
        range will result in a TraitError.

    minimum_date : Date
        The minimum date available in the calendar. If not defined then
        the default value is September 14, 1752.

    maximum_date : Date
        The maximum date available in the calendar. If not defined then
        the default value is December 31, 7999.

    selected : Event
        Triggered whenever the user clicks or changes the control. The
        event payload will be the date on the control.

    activated : Event
        Triggered whenever the user activates a new date via double
        click or pressing enter. The event payload will be the date
        on the control.

    """
    minimum_date = Date(datetime.date(1752, 9, 14))

    maximum_date = Date(datetime.date(7999, 12, 31))

    date = Bounded(datetime.date.today(), low='minimum_date', high='maximum_date')

    selected = Event

    activated = Event

    #---------------------------------------------------------------------------
    # Overridden parent traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ICalendarImpl)


Calendar.protect('selected', 'activated')

