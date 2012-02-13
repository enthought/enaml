#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .styling import wx_color_from_color, wx_font_from_font

from ..stylable import AbstractTkStylable


class WXStylable(AbstractTkStylable):
    """ A Wx implementation of Stylable.

    """
    #: A flag used to indicate that the instance has a font which is
    #: different from its default value.
    _has_default_wx_font = True
     
    def initialize(self):
        """ Initialize the attributes of the underlying widget.

        """
        super(WXStylable, self).initialize()
        shell = self.shell_obj
        if shell.bg_color:
            self.set_bg_color(shell.bg_color)
        if shell.fg_color:
            self.set_fg_color(shell.fg_color)
        if shell.font:
            self.set_font(shell.font)
    
    #--------------------------------------------------------------------------
    # Shell Object Change Handlers 
    #--------------------------------------------------------------------------
    def shell_bg_color_changed(self, color):
        """ The change handler for the 'bg_color' attribute on the shell
        object. Sets the background color of the internal widget to the 
        given color.
        
        """
        self.set_bg_color(color)
    
    def shell_fg_color_changed(self, color):
        """ The change handler for the 'fg_color' attribute on the shell
        object. Sets the foreground color of the internal widget to the 
        given color.

        """
        self.set_fg_color(color)

    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the shell 
        object. Sets the font of the internal widget to the given font.

        """
        self.set_font(font)

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_bg_color(self, color):
        """ Sets the background color of the widget to an appropriate
        wxColor given the provided Enaml Color object.

        """
        wx_color = wx_color_from_color(color)
        self.widget.SetBackgroundColour(wx_color)

    def set_fg_color(self, color):
        """ Sets the foreground color of the widget to an appropriate
        wxColor given the provided Enaml Color object.

        """
        wx_color = wx_color_from_color(color)
        self.widget.SetForegroundColour(wx_color)

    def set_font(self, font):
        """ Sets the font of the widget to an appropriate QFont given 
        the provided Enaml Font object.

        """
        # There's no such thing as a NullFont on wx, so if the font is
        # equivalent to the Enaml default font, and we haven't yet changed 
        # the font for this instance, then we don't change it. Otherwise
        # the fonts won't be equivalelnt to the default.
        if not font and self._has_default_wx_font:
            return

        wx_font = wx_font_from_font(font)
        self.widget.SetFont(wx_font)
        self._has_default_wx_font = False

