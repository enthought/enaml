#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QRadioButton
from .qt_abstract_button import QtAbstractButton


class QtRadioButton(QtAbstractButton):
    """ A Qt4 implementation of an Enaml RadioButton.

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QRadioButton(self.parent_widget)

