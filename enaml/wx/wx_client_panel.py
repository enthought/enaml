#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_proxy_widget import WxProxyWidget
from .wx_widget_component import WxWidgetComponent

class WxClientPanel(WxProxyWidget, WxWidgetComponent):
    """ A Wx implementation of an Enaml ClientPanel.

    """
    _central_widget_id = None
    _central_widget = None

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(WxClientPanel, self).create(tree)
        self.set_central_widget_id(tree['central_widget_id'])
 
    def init_layout(self):
        """ Perform layout initialization for the control.

        """
        child = self.find_child(self._central_widget_id)
        if child is not None:
            self.set_central_widget(child)
            
    def set_central_widget_id(self, widget_id):
        """ Set the central widge id for the window.

        """
        self._central_widget_id = widget_id

    def set_central_widget(self, child):
        sizer = self.widget().GetSizer()
        self._central_widget = child.widget()
        sizer.Add(self._central_widget)
        # if we have a native parent, relayout
        parent = self.widget().GetParent()
        if parent is not None:
            parent.Layout()
