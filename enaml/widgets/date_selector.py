#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Bool, Str, observe

from enaml.core.declarative import d_properties

from .bounded_date import BoundedDate


@d_properties('date_format', 'calendar_popup')
class DateSelector(BoundedDate):
    """ A widget to edit a Python datetime.date object.

    A DateSelector displays a Python datetime.date using an appropriate
    toolkit specific control. This is a geometrically smaller control
    than what is provided by Calendar.

    """
    #: A python date format string to format the date for display. If
    #: If none is supplied (or is invalid) the system locale setting
    #: is used. This may not be supported by all backends.
    date_format = Str()

    #: Whether to use a calendar popup for selecting the date.
    calendar_popup = Bool(False)

    def _default_hug_width(self):
        """ A DateSelector can expand freely in width by default.

        """
        return 'ignore'

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(DateSelector, self).snapshot()
        snap['date_format'] = self.date_format
        snap['calendar_popup'] = self.calendar_popup
        return snap

    @observe(r'^(date_format|calendar_popup)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass implementation is sufficient.
        super(DateSelector, self).send_member_change(change)

