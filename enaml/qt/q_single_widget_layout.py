#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QLayout


class QSingleWidgetLayout(QLayout):
    """ A QLayout subclass which can have at most one layout item.

    The layout item is expanded to fit the allowable space. This is
    similar to how central widgets behave in a QMainWindow.

    """
    #: An invalid size to use if there is no layout item.
    _invalid_size = QSize()

    #: Storage for the generated layout item.
    _layout_item = None

    def addItem(self, item):
        """ A virtual method implementation which sets the layout item
        in the layout. Any old item will be overridden.

        """
        self._layout_item = item
        self.update()

    def addWidget(self, widget):
        """ An overridden method which removes the old layout widget
        before adding the new one.

        This method can be safetly called with None as the widget
        argument.

        """
        self.takeAt(0)
        if widget is not None:
            widget.show()
            super(QSingleWidgetLayout, self).addWidget(widget)

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
            if res is not None:
                old = res.widget()
                if old is not None:
                    old.hide()
            return res

    def sizeHint(self):
        """ A virtual method implementation which returns an invalid
        size hint for the top-level Window.

        """
        item = self._layout_item
        if item is not None:
            return item.widget().sizeHint()
        return self._invalid_size

    def setGeometry(self, rect):
        """ A reimplemented method which sets the geometry of the managed
        widget to fill the given rect.

        """
        super(QSingleWidgetLayout, self).setGeometry(rect)
        item = self._layout_item
        if item is not None:
            item.widget().setGeometry(rect)

    def minimumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        item = self._layout_item
        if item is not None:
            return item.widget().minimumSizeHint()
        return super(QSingleWidgetLayout, self).minimumSize()

    def maximumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        item = self._layout_item
        if item is not None:
            return item.widget().maximumSize()
        return super(QSingleWidgetLayout, self).maximumSize()

