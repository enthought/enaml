#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements

from .qt.QtGui import QFormLayout
from .qt_container import QtContainer

from ..form import IFormImpl


class QtForm(QtContainer):

    implements(IFormImpl)

    def create_widget(self):
        self.widget = QFormLayout()

    def initialize_widget(self):
        pass
    
    def layout_child_widgets(self):
        layout = self.widget
        for child in self.parent.children:
            name = child.name
            child_widget = child.toolkit_widget()
            layout.addRow(name, child_widget)

    def child_name_updated(self, child, name):
        layout = self.widget
        control = child.toolkit_widget()
        label = layout.labelForField(control)
        if label:
            label.setText(name)

