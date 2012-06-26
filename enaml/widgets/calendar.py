#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.core.trait_types import EnamlEvent

from .bounded_date import BoundedDate


class Calendar(BoundedDate):
    """ A bounded date control which edits a Python datetime.date using 
    a widget which resembles a calendar.

    """
    #: An event triggered when the user clicks or changes the control
    #: from the user interface. The event payload will be the date
    #: selected in the control.
    selected = EnamlEvent

    #: An event triggered whenever the user activates a new date by
    #: double clicking or pressing enter on the user interface. The event
    #: payload will be the date activated in the control.
    activated = EnamlEvent

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def receive_selected(self, ctxt):
        """ Callback from the UI when the control is selected.

        """
        self.selected(ctxt['value'])

    def receive_activated(self, ctxt):
        """ Callback from the UI when the control is activated.

        """
        self.activated(ctxt['value'])

