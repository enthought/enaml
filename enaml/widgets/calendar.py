#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Event, Instance

from .bounded_date import BoundedDate, AbstractTkBoundedDate


class AbstractTkCalendar(AbstractTkBoundedDate):
    pass


class Calendar(BoundedDate):
    """ A calendar widget.

    A Calendar displays a Python datetime.date using an appropriate
    toolkit specific control.

    """
    #: Triggered whenever the user clicks or changes the control. The
    #: event payload will be the date on the control. This is event is
    #: also fired when the value of :attr:`date` is set programmatically.
    selected = Event

    #: Triggered whenever the user activates a new date via double
    #: click or pressing enter. The event payload will be the date
    #: on the control.
    activated = Event

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkCalendar)

