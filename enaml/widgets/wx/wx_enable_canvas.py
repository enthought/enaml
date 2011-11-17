#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enable.api import Window as EnableWindow

from .wx_control import WXControl

from ..enable_canvas import AbstractTkEnableCanvas


class WXEnableCanvas(WXControl, AbstractTkEnableCanvas):
    """ A wxPython implementation of EnableCanvas

    """
    #: The EnableWindow that is created to hold the component
    window = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates an EnableWindow instance to hold the component and
        uses that instance control as the toolkit widget. This assumes
        that enable picks the appropriate toolkit backend.

        """
        component = self.shell_obj.component
        self.window = EnableWindow(self.parent_widget(), component=component)
        self.widget = self.window.control

    def shell_component_changed(self, component):
        """ The change handler for the 'component' attribute on the 
        shell object.

        """
        raise NotImplementedError('changing components not yet supported')

