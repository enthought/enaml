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
        self._set_title(shell.title)
        self._set_icon(shell.icon)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute on the shell 
        object.

        """
        self._set_title(title)
    
    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute on the shell
        object.

        """
        self._set_icon(icon)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def _set_title(self, title):
        """ Sets the title of this tab in the parent tab widget.

        """
        # We can't use widget.parent() here to retrieve the tab widget,
        # though it is tempting. This is because the TabWidget maintains
        # an internal QStackedWidget control which is actually the parent
        # of the tab, and that stacked widget doesn't have the methods we
        # want to use. So, we get at the tab widget by going to the parent
        # of our shell object.
        widget = self.widget
        tab_widget = self.shell_obj.parent.toolkit_widget
        idx = tab_widget.indexOf(widget)
        if idx != -1:
            tab_widget.setTabText(idx, title)
     
    def _set_icon(self, icon):
        """ Sets the icon of this tab in the parent tab widget.

        """
        # XXX handle icons
        pass

