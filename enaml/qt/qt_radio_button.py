#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QRadioButton
from .qt_abstract_button import QtAbstractButton


class QtRadioButton(QtAbstractButton):
    """ A Qt implementation of an Enaml RadioButton.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying radio button widget.

        """
        return QRadioButton(parent)

