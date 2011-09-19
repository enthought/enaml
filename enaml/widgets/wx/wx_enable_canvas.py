#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements, Instance
from enable.api import Window as EnableWindow

from .wx_control import WXControl

from ..enable_canvas import IEnableCanvasImpl


class WXEnableCanvas(WXControl):

    implements(IEnableCanvasImpl)

    window = Instance(EnableWindow)

    def create_widget(self):
        component = self.parent.component
        self.window = EnableWindow(self.parent_widget(), component=component)
        self.widget = self.window.control
        
    def initialize_widget(self):
        pass
    
    def init_meta_handlers(self):
        pass

    def parent_component_changed(self, component):
        # XXX implement me
        pass

