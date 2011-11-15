# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
from .wx_container import WXContainer
from ..window import AbstractTkWindow


class WXWindow(WXContainer, AbstractTkWindow):
    """ A wxPython implementation of a Window.

    WXWindow uses a combined set of wx.Frame - wx.Window widget to create
    a simple top level window which contains other child widgets and
    layouts. Because of this dual behaviour some enaml calls need
    to be delegated to the wx.Frame and some to the wx.Window.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.Frame control.

        """
        # FIXME: this is an ugly hack since the wx.Frame does not show
        # well. It is advised in the wxWidget documentation to add a
        # Panel or Window control before adding the children.
        self._frame = wx.Frame(self.parent_widget())
        self.widget = wx.Window(self._frame)

    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        super(WXWindow, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def show(self):
        """ Displays the window to the screen.

        """
        self._frame.Show()

    def hide(self):
        """ Hide the window from the screen.

        """
        self._frame.Hide()

    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute.

        """
        self.set_title(title)

    def set_title(self, title):
        """ Sets the title of the frame.

        """
        self._frame.SetTitle(title)
    
    def size(self):
        """ Overridden parent class method to take into account the
        size of the frame decoration.

        """
        return self._frame.GetClientSizeTuple()
    
    def resize(self, width, height):
        """ Overridden parent class method to take into account the
        size of the frame decoration.

        """
        self._frame.SetClientSize((width, height))
    
    def set_min_size(self, min_width, min_height):
        """ Overridden parent class method to take into account the
        size of the frame decoration.

        """
        frame = self._frame
        frame_width, frame_height = frame.GetSizeTuple()
        client_width, client_height = frame.GetClientSizeTuple() 
        min_width = min_width + frame_width - client_width
        min_height = min_height + frame_height - client_height
        frame.SetSizeHints(min_width, min_height)
        
    def move(self, x, y):
        """ Overridden parent class method to move the frame rather
        than its internal Window.

        """
        self._frame.MoveXY(x, y)
        
    # XXX we still need to handle geometry() and set_geometry()
    # to deal with frame decorations properly
    
