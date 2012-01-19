#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enable.api import Window as EnableWindow

from .qt_control import QtControl

from ..enable_canvas import AbstractTkEnableCanvas


class QtEnableCanvas(QtControl, AbstractTkEnableCanvas):
    """ A Qt implementation of EnableCanvas

    """
    #: The EnableWindow that is created to hold the component
    window = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates an EnableWindow instance to hold the component and
        uses that instance control as the toolkit widget. This assumes
        that enable picks the appropriate toolkit backend.

        """
        component = self.shell_obj.component
        self.window = EnableWindow(parent, component=component)
        self.widget = self.window.control
        # XXX Enable window doesn't parent on Qt (this is already fixed in Enable trunk)
        self.widget.setParent(parent)

    def shell_component_changed(self, component):
        """ The change handler for the 'component' attribute on the 
        shell object.

        """
        raise NotImplementedError('changing components not yet supported')

    def size_hint(self):
        """ A reimplemented parent class method to retrieve the 
        size hint as the preferred size from the enable component.

        """
        return self.shell_obj.component.get_preferred_size()

