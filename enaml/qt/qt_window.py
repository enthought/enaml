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
    """ A Qt implementation of a window

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QWidget(self.parent_widget)
        self.widget.setLayout(QtWindowLayout())

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        super(QtWindow, self).initialize(init_attrs)
        self.set_title(init_attrs.get('title', ''))

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ Adds the central widget to the window layout.

        """
        # XXX this a temporary hack until we decide on the central widget
        # of a window
        super(QtWindow, self).initialize_layout()
        if len(self.children) > 0:
            self.widget.layout().addWidget(self.children[0].widget)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_close(self, ctxt):
        """ Message handler for close

        """
        return self.close()

    def receive_maximize(self, ctxt):
        """ Message handler for maximize

        """
        return self.maximize()

    def receive_minimize(self, ctxt):
        """ Message handler for minimize

        """
        return self.minimize()

    def receive_restore(self, ctxt):
        """ Message handler for restore

        """
        return self.restore()

    def receive_show(self, ctxt):
        """ Message handler for show

        """
        return self.show()

    def receive_set_icon(self, ctxt):
        """ Message handler for set_icon

        """
        return NotImplemented

    def receive_set_title(self, ctxt):
        """ Message handler for set_title

        """
        return self.set_title(ctxt.get('title', ''))
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget.close()
        return True

    def maximize(self):
        """ Maximize the window.

        """
        self.widget.showMaximized()
        return True

    def minimize(self):
        """ Minimize the window.

        """
        self.widget.showMinimized()
        return True

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget.showNormal()
        return True

    def show(self):
        """ Show the widget

        """
        self.set_visible(True)
        return True

    def set_icon(self, icon):
        """ Set the window icon.

        """
        return NotImplemented

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget.setWindowTitle(title)
        return True
