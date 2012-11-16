#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str

from .bounded_date import BoundedDate


class DateSelector(BoundedDate):
    """ A widget to edit a Python datetime.date object.

    A DateSelector displays a Python datetime.date using an appropriate
    toolkit specific control. This is a geometrically smaller control
    than what is provided by Calendar.

    """
    #: A python date format string to format the date for display. If
    #: If none is supplied (or is invalid) the system locale setting
    #: is used. This may not be supported by all backends.
    date_format = Str

    #: Whether to use a calendar popup for selecting the date.
    calendar_popup = Bool(False)

    #: How strongly to hugs the content width. A DateSelector ignores
    #: the width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(DateSelector, self).snapshot()
        snap['date_format'] = self.date_format
        snap['calendar_popup'] = self.calendar_popup
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(DateSelector, self).bind()
        self.publish_attributes('date_format', 'calendar_popup')

