#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from enaml.core.trait_types import EnamlEvent

from .bounded_date import BoundedDate


class DateEdit(BoundedDate):
    """ A widget to edit a Python datetime.date object.

    A DateEdit displays a Python datetime.date using an appropriate
    toolkit specific control. This is a geometrically smaller control 
    than what is provided by Calendar.

    """
    #: A python date format string to format the date. If none is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    date_format = Str

    #: Triggered whenever the user changes the date through the ui
    #: control, but not programmatically. The event payload will be 
    #: the current date on the control.
    date_changed = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. DateEdits 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(DateEdit, self).bind()
        self.default_send('date_format')

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(DateEdit, self).initial_attrs()
        attrs = {'date_format': self.date_format}
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def receive_date_changed(self, ctxt):
        """ Callback from the UI when the date value is changed.

        """
        date = ctxt['value']
        self.set_guarded(date=date)
        self.date_changed(date)

