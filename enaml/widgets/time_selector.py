#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Str, observe

from enaml.core.declarative import d_properties

from .bounded_time import BoundedTime


@d_properties('time_format')
class TimeSelector(BoundedTime):
    """ A time widget that displays a Python datetime.time object using
    an appropriate toolkit specific control.

    """
    #: A python time format string to format the time. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    time_format = Str()

    def _default_hug_width(self):
        """ A TimeSelector is free to expand in width and height.

        """
        return 'ignore'

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(TimeSelector, self).snapshot()
        snap['time_format'] = self.time_format
        return snap

    @observe('time_format', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass implementation is sufficient.
        super(TimeSelector, self).send_member_change(change)

