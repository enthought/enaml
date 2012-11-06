#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from .bounded_time import BoundedTime


class TimeSelector(BoundedTime):
    """ A time widget that displays a Python datetime.time object using
    an appropriate toolkit specific control.

    """
    #: A python time format string to format the time. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    time_format = Str

    #: How strongly to hugs the content width. A TimeSelector ignores
    #: the width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(TimeSelector, self).snapshot()
        snap['time_format'] = self.time_format
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TimeSelector, self).bind()
        self.publish_attributes('time_format')

