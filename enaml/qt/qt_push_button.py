#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QPushButton
from .qt_abstract_button import QtAbstractButton


class QtPushButton(QtAbstractButton):
    """ A Qt implementation of an Enaml PushButton.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying QPushButton widget.

        """
        return QPushButton(parent)

