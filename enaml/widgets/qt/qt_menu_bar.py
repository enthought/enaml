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

    def initialize(self):
        """ Initializes the QMenuBar.

        """
        super(QtMenuBar, self).initialize()
        self.update_menus()

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def shell_menus_changed(self):
        """ The change handler for the 'menus' attribute on the shell
        object.

        """
        self.update_menus()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def update_menus(self):
        """ Updates the menu bar with the child menu objects.

        """
        # There is no need to clear() the Menu since that destroys the
        # underlying objects, and any dynamic children will have already
        # been destroyed. It's sufficient to just make a pass over the 
        # menus and add them to the menu bar. Qt is smart enough to do 
        # the right thing here.
        widget = self.widget
        for menu in self.shell_obj.menus:
            widget.addMenu(menu.toolkit_widget)
              
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

