#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_component import QtComponent

from ..menu_bar import AbstractTkMenuBar


class QtMenuBar(QtComponent, AbstractTkMenuBar):
    """ A Qt4 implementation of a MenuBar.

    """
    def create(self, parent):
        """ Creates the underlying QMenuBar.

        """
        self.widget = QtGui.QMenuBar(parent)

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_bg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenuBar.

        """
        pass
    
    def set_fg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenuBar.

        """
        pass
    
    def set_font(self, font):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenuBar.

        """
        pass

