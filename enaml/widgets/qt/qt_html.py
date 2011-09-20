#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_control import QtControl

from ..html import IHtmlImpl


class QtHtml(QtControl):
    """ A Qt implementation of Html.

    See Also
    --------
    Html
    
    """
    implements(IHtmlImpl)

    #---------------------------------------------------------------------------
    # IHtmlImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying widget to display HTML.

        """
        self.widget = QtGui.QTextEdit(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        self.widget.setReadOnly(True)
        self.set_page_source(self.parent.source)

    def parent_source_changed(self, source):
        """ The change handler for the 'source' attribute. Not meant for
        public consumption.

        """
        self.set_page_source(source)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def set_page_source(self, source):
        """ Sets the page source for the underlying control. Not meant 
        for public consumption.

        """
        self.widget.setHtml(source)

