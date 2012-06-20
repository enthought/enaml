#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, on_trait_change

from .bounded_datetime import BoundedDatetime

from ..core.trait_types import EnamlEvent


class DatetimeEdit(BoundedDatetime):
    """ A datetime widget that displays a Python datetime.datetime object 
    using an appropriate toolkit specific control.

    """
    #: A python date format string to format the datetime. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    datetime_format = Str

    #: Triggered whenever the user changes the date through the ui
    #: control, but not programmatically. The event payload will be 
    #: the datetime on the control.
    datetime_changed = EnamlEvent
    
    #: How strongly a component hugs its contents' width. DatetimeEdits 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    @on_trait_change('datetime_format')
    def sync_object_state(self, name, new):
        msg = 'set_' + name
        self.send(msg, {'value':new})

    def initial_attrs(self):
        super_attrs = super(BoundedDatetime, self).initial_attrs()
        attrs = {'datetime_format':self.datetime_format}
        attrs.update(super_attrs)
        return attrs

