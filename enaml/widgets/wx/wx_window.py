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
    _initializing = False

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
        self.widget = wx.Panel(self._frame)

    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        self._initializing = True
        try:
            super(WXWindow, self).initialize()
            self.set_title(self.shell_obj.title)
        finally:
            self._initializing = False

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute.

        """
        self.set_title(title)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Sets the title of the frame.

        """
        self._frame.SetTitle(title)
    
    def set_visible(self, visible):
        """ Overridden from the parent class to raise the window to
        the front if it should be shown.

        """
        # Don't show the window if we're not initializing.
        if not self._initializing:
            if visible:
                # Wx doesn't reliably emit resize events when making a 
                # ui visible. So this extra call to update cns helps make 
                # sure things are arranged nicely.
                self.shell_obj.set_needs_update_constraints()
                self._frame.Show()
            else:
                self._frame.Hide()

    #--------------------------------------------------------------------------
    # Overridden Geometry Methods 
    #--------------------------------------------------------------------------
    def resize(self, width, height):
        """ Overridden parent class method to do the resize on the 
        internal wx.Frame object.

        """
        self._resize(self._frame, width, height)
    
    def min_size(self):
        """ Overridden parent class method to get the min size on 
        the internal wx.Frame object.

        """
        return self._min_size(self._frame)
        
    def set_min_size(self, min_width, min_height):
        """ Overridden parent class method to set the min size on the
        internal wx.Frame object.

        """
        self._set_min_size(self._frame, min_width, min_height)
        
    def pos(self):
        """ Overridden parent class method to get the position of
        the internal wx.Frame object.

        """
        return self._pos(self._frame)

    def move(self, x, y):
        """ Overridden parent class method to do the move on the internal
        wx.Frame object.

        """
        self._move(self._frame, x, y)
        
    def frame_geometry(self):
        """ Overridden parent class method to get the frame geometry
        of the internal wx.Frame object.

        """
        return self._frame_geometry(self._frame)

    def geometry(self):
        """ Overridden parent class method to get the geometry
        of the internal wx.Frame object.

        """
        return self._geometry(self._frame)
    
    def set_geometry(self, x, y, width, height):
        """ Overridden parent class method to set the geometry
        of the internal wx.Frame object.

        """
        self._set_geometry(self._frame, x, y, width, height)

