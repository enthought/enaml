#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QWidget, QLayout
from .qt_widget_component import QtWidgetComponent


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


class QtWindow(QtWidgetComponent):
    """ A Qt4 implementation of an Enaml Window.

    """
    def create(self):
        """ Create the underlying QWidget object.

        """
        self.widget = QWidget(self.parent_widget)
        self.widget.setLayout(QtWindowLayout())

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtWindow, self).initialize(attrs)
        self.set_title(attrs.get('title', ''))
        self.set_initial_size(attrs.get('initial_size', (-1, -1)))

    def post_initialize(self):
        """ Perform the post initialization work.

        For a QtWindow, this involves adding the the central widget
        to the window layout.

        """
        super(QtWindow, self).post_initialize()
        children = self.children
        if len(children) > 0:
            central_widget = children[0].widget
            self.widget.layout().addWidget(central_widget)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_close(self, payload):
        """ Message handler for the 'close' action.

        """
        self.close()

    def on_message_maximize(self, payload):
        """ Message handler for the 'maximize' action.

        """
        self.maximize()

    def on_message_minimize(self, payload):
        """ Message handler for the 'minimize' action.

        """
        self.minimize()

    def on_message_restore(self, payload):
        """ Message handler for the 'restore' action.

        """
        self.restore()

    def on_message_set_icon(self, payload):
        """ Message handler for the 'set-icon' action.

        """
        pass

    def on_message_set_title(self, payload):
        """ Message handler for the 'set-title' action.

        """
        self.set_title(payload['title'])
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget.close()

    def maximize(self):
        """ Maximize the window.

        """
        self.widget.showMaximized()

    def minimize(self):
        """ Minimize the window.

        """
        self.widget.showMinimized()

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget.showNormal()

    def set_icon(self, icon):
        """ Set the window icon.

        """
        pass 

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget.setWindowTitle(title)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        if -1 in size:
            return
        self.widget.resize(*size)

