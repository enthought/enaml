#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Bool, Str, observe

from enaml.core.declarative import d_properties

from .bounded_datetime import BoundedDatetime


@d_properties('datetime_format', 'calendar_popup')
class DatetimeSelector(BoundedDatetime):
    """ A datetime widget that displays a Python datetime.datetime
    object using an appropriate toolkit specific control.

    """
    #: A python date format string to format the datetime. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    datetime_format = Str()

    #: Whether to use a calendar popup for selecting the date.
    calendar_popup = Bool(False)

    def _default_hug_width(self):
        """ A DatetimeSelector can expand freely in width by default.

        """
        return 'ignore'

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(DatetimeSelector, self).snapshot()
        snap['datetime_format'] = self.datetime_format
        snap['calendar_popup'] = self.calendar_popup
        return snap

    @observe(r'^(datetime_format|calendar_popup)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass implementation is sufficient.
        super(DatetimeSelector, self).send_member_change(change)

