#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..html import AbstractTkHtml


class QtHtml(QtControl, AbstractTkHtml):
    """ A Qt implementation of Html.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying widget to display HTML.

        """
        self.widget = QtGui.QTextEdit(parent)

    def initialize(self):
        """ Initializes the attributes of the control.

        """
        super(QtHtml, self).initialize()
        self.widget.setReadOnly(True)
        self.set_page_source(self.shell_obj.source)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_source_changed(self, source):
        """ The change handler for the 'source' attribute.

        """
        self.set_page_source(source)

    def set_page_source(self, source):
        """ Sets the page source for the underlying control.

        """
        self.widget.setHtml(source)

