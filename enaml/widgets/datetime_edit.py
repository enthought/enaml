#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from .bounded_datetime import BoundedDatetime


class DatetimeEdit(BoundedDatetime):
    """ A datetime widget that displays a Python datetime.datetime 
    object using an appropriate toolkit specific control.

    """
    #: A python date format string to format the datetime. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    datetime_format = Str

    #: How strongly a component hugs its contents' width. DatetimeEdits 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(DatetimeEdit, self).creation_attributes()
        super_attrs['datetime_format'] = self.datetime_format
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(DatetimeEdit, self).bind()
        self.publish_attributes('datetime_format')

