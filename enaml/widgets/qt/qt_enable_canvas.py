#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enable.api import Window as EnableWindow

from .qt_control import QtControl

from ..enable_canvas import AbstractTkEnableCanvas


class QtEnableCanvas(QtControl, AbstractTkEnableCanvas):

    window = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        component = self.shell_obj.component
        self.window = EnableWindow(self.parent_widget(), component=component)
        self.widget = self.window.control
        
    def shell_component_changed(self, component):
        # XXX implement me
        print 'changing components not yet supported'

