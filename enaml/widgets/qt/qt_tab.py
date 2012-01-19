#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_container import QtContainer

from ..tab import AbstractTkTab


class QtTab(QtContainer, AbstractTkTab):
    """ A Qt implementation of the Tab component.
    
    """
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initialize the attributes of the tab.

        """
        super(QtTab, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_icon(shell.icon)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute on the shell 
        object.

        """
        self.set_title(title)
    
    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute on the shell
        object.

        """
        self.set_icon(icon)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Sets the title of this tab in the parent tab widget.

        """
        # We use widget.parent().parent() here to retrieve the tab 
        # widget. This is because the TabWidget maintains an internal 
        # QStackedWidget control which is actually the parent of the tab.
        widget = self.widget
        tab_widget = widget.parent().parent()
        idx = tab_widget.indexOf(widget)
        if idx != -1:
            tab_widget.setTabText(idx, title)
     
    def set_icon(self, icon):
        """ Sets the icon of this tab in the parent tab widget.

        """
        # XXX handle icons
        pass

