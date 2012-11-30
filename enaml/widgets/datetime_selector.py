#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str

from .bounded_datetime import BoundedDatetime


class DatetimeSelector(BoundedDatetime):
    """ A datetime widget that displays a Python datetime.datetime
    object using an appropriate toolkit specific control.

    """
    #: A python date format string to format the datetime. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    datetime_format = Str

    #: Whether to use a calendar popup for selecting the date.
    calendar_popup = Bool(False)

    #: How strongly to hugs the content width. A DatetimeSelector ignores
    #: the width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(DatetimeSelector, self).snapshot()
        snap['datetime_format'] = self.datetime_format
        snap['calendar_popup'] = self.calendar_popup
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(DatetimeSelector, self).bind()
        self.publish_attributes('datetime_format', 'calendar_popup')

