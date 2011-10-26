#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..label import AbstractTkLabel


class QtLabel(QtControl, AbstractTkLabel):
    """ A Qt implementation of Label.

    A QtLabel displays static text using a QLabel control.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying text control.

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
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.set_label(text)
        # XXX we might need a relayout call here when the text changes
        # since it's width may have changed and the size hint may 
        # now be different. We probably want to make it configurable
        # though since fixed width labels don't need a relayout

    def set_label(self, label):
        """ Sets the label on the underlying control. Not meant for
        public consumption.

        """
        self.widget.setText(label)

