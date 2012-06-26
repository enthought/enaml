#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QCheckBox
from .qt_abstract_button import QtAbstractButton


class QtCheckBox(QtAbstractButton):
    """ A Qt4 implementation of an Enaml CheckBox.

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QCheckBox(self.parent_widget)

