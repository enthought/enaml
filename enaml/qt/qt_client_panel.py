#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_proxy_widget import QtProxyWidget
from .qt_widget_component import QtWidgetComponent

class QtClientPanel(QtProxyWidget, QtWidgetComponent):
    """ A Qt implementation of an Enaml ClientPanel.

    """
    _central_widget_id = None
    _central_widget = None

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtClientPanel, self).create(tree)
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
        layout = self.widget().layout()
        layout.removeWidget(self._central_widget)
        self._central_widget = child.widget()
        layout.addWidget(self._central_widget)
