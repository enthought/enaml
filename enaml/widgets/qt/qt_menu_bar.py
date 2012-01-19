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
        # We ignore the parent when creating the menu bar. The parent 
        # main window is repsonsible for setting the menu bar on itself, 
        # and using the parent here causes issues on certain platforms.
        self.widget = QtGui.QMenuBar()

    def initialize(self):
        """ Initializes the QMenuBar.

        """
        super(QtMenuBar, self).initialize()
        self.update_menus()

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def shell_menus_changed(self, menus):
        """ Update the menu bar with the new list of menu objects.

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

