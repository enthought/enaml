#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .styling import q_color_from_color, q_font_from_font
from .qt import QtGui

from ..stylable import AbstractTkStylable


class QtStylable(AbstractTkStylable):
    """ A Qt4 implementation of Stylable.

    """
    def initialize(self):
        """ Initialize the attributes of the underlying widget.

        """
        super(QtStylable, self).initialize()
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
        QColor given the provided Enaml Color object.

        """
        widget = self.widget
        role = widget.backgroundRole()
        if not color:
            palette = QtGui.QApplication.instance().palette(widget)
            qcolor = palette.color(role)
            # On OSX, the default color is rendered *slightly* off
            # so a simple workaround is to tell the widget not to
            # auto fill the background.
            widget.setAutoFillBackground(False)
        else:
            qcolor = q_color_from_color(color)
            # When not using qt style sheets to set the background
            # color, we need to tell the widget to auto fill the 
            # background or the bgcolor won't render at all.
            widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

    def set_fg_color(self, color):
        """ Sets the foreground color of the widget to an appropriate
        QColor given the provided Enaml Color object.

        """
        widget = self.widget
        role = widget.foregroundRole()
        if not color:
            palette = QtGui.QApplication.instance().palette(widget)
            qcolor = palette.color(role)
        else:
            qcolor = q_color_from_color(color)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

    def set_font(self, font):
        """ Sets the font of the widget to an appropriate QFont given 
        the provided Enaml Font object.

        """
        q_font = q_font_from_font(font)
        self.widget.setFont(q_font)

