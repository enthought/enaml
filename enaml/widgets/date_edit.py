#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, on_trait_change

from .bounded_date import BoundedDate

from ..core.trait_types import EnamlEvent


class DateEdit(BoundedDate):
    """ A widget to edit a Python datetime.date object.

    A DateEdit displays a Python datetime.date using an appropriate
    toolkit specific control. This is a geometrically smaller control 
    than what is provided by Calendar.

    """
    #: A python date format string to format the date. If none is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by allo backends.
    date_format = Str

    #: Triggered whenever the user changes the date through the ui
    #: control, but not programmatically. The event payload will be 
    #: the date on the control.
    date_changed = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. DateEdits 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def inital_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(DateEdit, self).inital_attrs()
        attrs = {
            'date_format' : self.date_format,
        }
        super_attrs.update(attrs)
        return super_attrs

    def receive_date_changed(self, context):
        """ Callback from the UI when the date value is changed.

        """
        self._setting = True
        self.date = context['value']
        self._setting = False
        self.date_changed(self.date)

    @on_trait_change('date_format')
    def update_date_format(self):
        """ Notify the client component of updates to the date format.

        """
        self.send('set_date_format', {'value':self.date_format})

