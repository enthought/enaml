#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_window import WXWindow

from ..main_window import AbstractTkMainWindow


class  WXMainWindow(WXWindow, AbstractTkMainWindow):
    """ A Wx implementation of a MainWindow.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying Wx main window object.

        """
        # The wxFrame created by the parent class is sufficient.
        super(WXMainWindow, self).create(parent)
    
    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        super(WXMainWindow, self).initialize()
        menu_bar = self.shell_obj.menu_bar
        if menu_bar is not None:
            self._frame.SetMenuBar(menu_bar.toolkit_widget)

