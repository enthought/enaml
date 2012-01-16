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
        self.update_contents()
    
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
        
    def shell_contents_changed(self, contents):
        """ The change handler for the 'contents' attribute on the shell
        object. 

        """
        self.update_contents()

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
    def update_contents(self):
        """ Updates the contents of the Menu.

        """
        # There is no need to clear() the Menu since that destroys the
        # underlying objects, and any dynamic children will have already
        # been destroyed. It's sufficient to just make a pass over the 
        # contents and add them to the menu. Qt is smart enough to do the
        # right thing here.
        widget = self.widget
        for item in self.shell_obj.contents:
            child_widget = item.toolkit_widget
            if isinstance(child_widget, QtGui.QMenu):
                widget.addMenu(child_widget)
            else:
                widget.addAction(child_widget)

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
