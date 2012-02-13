#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QRect
from .qt.QtGui import QWidgetItem

from ..sizable import AbstractTkSizable


class QtSizable(AbstractTkSizable):
    """ A Qt4 implementation of Sizable.

    """
    #: A class attribte which indicates whether or not to use a 
    #: QWidget item to compute the layout geometry. Subclasses
    #: should override as necessary to change the behavior. The 
    #: default is True. 
    use_widget_item_for_layout = True

    @property
    def _widget_item(self):
        """ A readonly cached property which returns the QWidgetItem
        for the underlying Qt widget.

        """
        try:
            res = self.__widget_item
        except AttributeError:
            res = self.__widget_item = QWidgetItem(self.widget)
        return res

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, ignoring
        any windowing decorations. This value is used by the layout 
        manager to determine how much space to allocate the widget.

        """
        if self.use_widget_item_for_layout:
            size_hint = self._widget_item.sizeHint()
        else:
            size_hint = self.widget.sizeHint()
        return (size_hint.width(), size_hint.height())

    def layout_geometry(self):
        """ Returns the (x, y, width, height) to of layout geometry
        info for the internal toolkit widget. This should ignore any
        windowing decorations, and may be different than the value
        returned by geometry() if the widget's effective layout rect
        is different from its paintable rect.

        """
        if self.use_widget_item_for_layout:
            geo = self._widget_item.geometry()
        else:
            geo = self.widget.geometry()
        return (geo.x(), geo.y(), geo.width(), geo.height())

    def set_layout_geometry(self, x, y, width, height):
        """ Sets the layout geometry of the internal widget to the 
        given x, y, width, and height values. The parameters passed
        are equivalent semantics to layout_geometry().

        """
        rect = QRect(x, y, width, height)
        if self.use_widget_item_for_layout:
            self._widget_item.setGeometry(rect)
        else:
            self.widget.setGeometry(rect)

    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, ignoring any windowing
        decorations.

        """
        geom = self.widget.geometry()
        return (geom.x(), geom.y(), geom.width(), geom.height())

    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        self.widget.setGeometry(x, y, width, height)

    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        min_size = self.widget.minimumSize()
        return (min_size.width(), min_size.height())

    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        self.widget.setMinimumSize(min_width, min_height)

    def max_size(self):
        """ Returns the hard maximum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized larger than this value

        """
        max_size = self.widget.maximumSize()
        return (max_size.width(), max_size.height())

    def set_max_size(self, max_width, max_height):
        """ Set the hard maximum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        larger than this value.

        """
        # The hard Qt limit is 16777215 (which is 2**24 - 1) and will
        # print warnings to the shell if we attemp to set a max size
        # over that amount. This can be attempted when a QtMainWindow
        # has a central widget size equal to max size, and it also has
        # a menu bar and other components. Clipping the max size like
        # this will not have an effect on layout computation and thus
        # is relatively safe.
        max_width = min(max_width, 16777215)
        max_height = min(max_height, 16777215)
        self.widget.setMaximumSize(max_width, max_height)

    def size(self):
        """ Returns the size of the internal toolkit widget, ignoring any
        windowing decorations, as a (width, height) tuple of integers.

        """
        size = self.widget.size()
        return (size.width(), size.height())
                
    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        self.widget.resize(width, height)

    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers, including any windowing decorations. 
        The coordinates should be relative to the origin of the widget's 
        parent, or to the screen if the widget is toplevel.

        """
        pos = self.widget.pos()
        return (pos.x(), pos.y())
            
    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        self.widget.move(x, y)

