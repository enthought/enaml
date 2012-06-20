#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_togglecontrol import QtToggleControl

class QtCheckBox(QtToggleControl):
      """ A Qt implementation of a check box

      """
      def create(self, parent):
            """ Create the underlying widget

            """
            self.widget = QtGui.QCheckBox(parent)

      def bind(self):
            """ Bind slots and signals

            """
            super(QtCheckBox, self).bind()

            self.widget.toggled.connect(self.on_toggled)
            self.widget.pressed.connect(self.on_pressed)
            self.widget.released.connect(self.on_released)
