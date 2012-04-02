#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QWidget, QLayout
from .qt_widget_component import QtWidgetComponent

from ...components.window import AbstractTkWindow


class QtWindowLayout(QLayout):
    """ A QLayout subclass which can have at most one layout item. This
    layout item is expanded to fit the allowable space, regardless of its
    size policy settings. This is similar to how central widgets behave 
    in a QMainWindow.

    The class is designed for use by QtWindow/QtDialog, other uses are at 
    the user's own risk.

    """
    def __init__(self, *args, **kwargs):
        super(QtWindowLayout, self).__init__(*args, **kwargs)
        self._layout_item = None
    
    def addItem(self, item):
        """ A virtual method implementation which sets the layout item
        in the layout. Any old item will be overridden.

        """
        self._layout_item = item
        self.update()

    def count(self):
        """ A virtual method implementation which returns 0 if no layout
        item is supplied, or 1 if there is a current layout item.

        """
        return 0 if self._layout_item is None else 1

    def itemAt(self, idx):
        """ A virtual method implementation which returns the layout item 
        for the given index or None if one does not exist.

        """
        if idx == 0:
            return self._layout_item

    def takeAt(self, idx):
        """ A virtual method implementation which removes and returns the
        item at the given index or None if one does not exist.

        """
        if idx == 0:
            res = self._layout_item
            self._layout_item = None
            return res
    
    def sizeHint(self):
        """ A reimplemented method to return a proper size hint for the
        layout, and hence the Window.

        """
        return QSize(600, 100)

    def setGeometry(self, rect):
        """ A reimplemented method which sets the geometry of the managed
        widget to fill the given rect.

        """
        super(QtWindowLayout, self).setGeometry(rect)
        item = self._layout_item
        if item is not None:
            item.widget().setGeometry(rect)


class QtWindow(QtWidgetComponent, AbstractTkWindow):
    """ A Qt4 implementation of Window.
     
    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying Qt widget.

        """
        self.widget = QWidget(parent)
        self.widget.setLayout(QtWindowLayout())

    def initialize(self):
        """ Intializes the attributes on the underlying Qt widget.

        """
        super(QtWindow, self).initialize()
        self.set_title(self.shell_obj.title)
        self.update_central_widget()

    #--------------------------------------------------------------------------
    # Abstract Toolkit Implementation
    #--------------------------------------------------------------------------
    def maximize(self):
        """ Maximizes the window to fill the screen.

        """
        self.widget.showMaximized()
            
    def minimize(self):
        """ Minimizes the window to the task bar.

        """
        self.widget.showMinimized()
            
    def restore(self):
        """ Restores the window after it has been minimized or maximized.

        """
        self.widget.showNormal()

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
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
        """ Updates the central widget in the dialog with the value from
        the shell object.

        """
        # It's possible for the central widget component to be None.
        # This must be allowed since the central widget may be generated
        # by an Include component, in which case it will not exist 
        # during initialization. However, we must have a central widget
        # for the Window, and so we just fill it with a dummy widget.
        central_widget = self.shell_obj.central_widget
        if central_widget is None:
            child_widget = QWidget()
        else:
            child_widget = central_widget.toolkit_widget
        self.widget.layout().addWidget(child_widget)

    def set_title(self, title):
        """ Sets the title of the underlying widget.

        """
        self.widget.setWindowTitle(title)

