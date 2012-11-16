#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QCheckBox
from .qt_abstract_button import QtAbstractButton


class QtCheckBox(QtAbstractButton):
    """ A Qt implementation of an Enaml CheckBox.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying check box widget.

        """
        return QCheckBox(parent)

