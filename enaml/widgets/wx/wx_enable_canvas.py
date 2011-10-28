#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enable.api import Window as EnableWindow

from .wx_control import WXControl

from ..enable_canvas import AbstractTkEnableCanvas


class WXEnableCanvas(WXControl, AbstractTkEnableCanvas):

    window = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        component = self.shell_obj.component
        self.window = EnableWindow(self.parent_widget(), component=component)
        self.widget = self.window.control

    def shell_component_changed(self, component):
        raise NotImplementedError('changing components not yet supported')

