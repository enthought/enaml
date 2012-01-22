#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_container import WXContainer

from ..tab import AbstractTkTab


class WXTab(WXContainer, AbstractTkTab):
    """ A wx implementation of the Tab component.
    
    """
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initialize the attributes of the tab.

        """
        super(WXTab, self).initialize()
        shell = self.shell_obj
        # We don't want to set the title during initialization on wx
        # because it will lead to segfaults (!). It's not a huge deal
        # however, because the title will be set when the tab is added
        # to the notebook.
        # self.set_title(shell.title)
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
        widget = self.widget
        tab_widget = self.shell_obj.parent.toolkit_widget
        for idx in range(tab_widget.GetPageCount()):
            if tab_widget.GetPage(idx) is widget:
                tab_widget.SetPageText(idx, title)
                break
     
    def set_icon(self, icon):
        """ Sets the icon of this tab in the parent tab widget.

        """
        # XXX handle icons
        pass

