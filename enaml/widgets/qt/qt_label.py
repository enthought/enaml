#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..label import AbstractTkLabel


class QtLabel(QtControl, AbstractTkLabel):
    """ A Qt implementation of Label.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QLabel control.

        """
        self.widget = QtGui.QLabel(self.parent_widget())

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(QtLabel, self).initialize()
        self.set_label(self.shell_obj.text)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)
        # If the text in the label changes, then the size hint of
        # label will have changed, and the layout system needs to
        # be informed.
        self.shell_obj.size_hint_updated = True

    def set_label(self, label):
        """ Sets the label on the underlying control.

        """
        self.widget.setText(label)

