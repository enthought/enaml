#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_component import WXComponent
from .wx_sizable import WXSizable

from ..window import AbstractTkWindow


class WXWindow(WXComponent, WXSizable, AbstractTkWindow):
    """ A wxPython implementation of a Window. It serves as a base class
    for WXMainWindow and WXDialog. It is not meant to be used directly.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying Wx widget.

        """
        msg = 'A WXWindow is a base class and cannot be used directly'
        raise NotImplementedError(msg)

    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        super(WXWindow, self).initialize()
        self.set_title(self.shell_obj.title)
        self.update_central_widget()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def maximize(self):
        """ Maximizes the window to fill the screen.

        """
        self.widget.Maximize(True)
            
    def minimize(self):
        """ Minimizes the window to the task bar.

        """
        self.widget.Iconize(True)
            
    def normalize(self):
        """ Restores the window after it has been minimized or maximized.

        """
        self.widget.Maximize(False)

    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute on the shell
        object.

        """
        self.set_title(title)
    
    def shell_central_widget_changed(self, central_widget):
        """ The change handler for the 'central_widget' attribute on 
        the shell object.

        """
        self.update_central_widget()
       
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def update_central_widget(self):
        """ Updates the central widget from the value on the shell 
        object. This method must be implemented by subclasses.

        """
        raise NotImplementedError

    def set_title(self, title):
        """ Sets the title of the frame.

        """
        self.widget.SetTitle(title)

