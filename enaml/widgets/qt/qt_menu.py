#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_component import QtComponent

from ..menu import AbstractTkMenu


class QtMenu(QtComponent, AbstractTkMenu):
    """ A Qt4 implementation of Menu.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QMenu object.

        """
        self.widget = QtGui.QMenu(parent)

    def initialize(self):
        """ Initialize the underlying QMenu object.

        """
        super(QtMenu, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)

        # It's not enough to simply create the menu with the proper
        # parent, we need to explicitly add the action or else it 
        # won't show up in a menu bar.
        parent = self.widget.parent()
        if parent is not None:
            # If the parent is not None, it's conceivable that its
            # a QMenuBar, so we can just duck-type here.
            parent.addMenu(self.widget)
    
    def bind(self):
        """ Binds the event handlers for the underlying QMenu object.

        """
        super(QtMenu, self).bind()
        widget = self.widget
        widget.aboutToShow.connect(self.on_about_to_show)
        widget.aboutToHide.connect(self.on_about_to_hide)

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def shell_title_changed(self, text):
        """ The change handler for the 'title' attribute on the shell
        object.

        """
        self.set_title(text)
    
    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_about_to_show(self):
        """ A signal handler for the 'aboutToShow' signal of the QMenu.

        """
        self.shell_obj.about_to_show = True

    def on_about_to_hide(self):
        """ A signal handler for the 'aboutToHide' signal of the QMenu.

        """
        self.shell_obj.about_to_hide = True

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Sets the title of the QMenu object.

        """
        self.widget.setTitle(title)

    def set_bg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenu.

        """
        pass
    
    def set_fg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenu.

        """
        pass
    
    def set_font(self, font):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenu.

        """
        pass

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def popup(self, pos=None, blocking=True):
        """ Pops up the menu at the appropriate position using a blocking
        context if requested.

        """
        if pos is None:
            pos = QtGui.QCursor.pos()
        else:
            pos = QtCore.QPoint(*pos)

        if blocking:
            self.widget.exec_(pos)
        else:
            self.widget.popup(pos)

