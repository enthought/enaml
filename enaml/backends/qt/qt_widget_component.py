#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QRect
from .qt.QtGui import QFrame, QWidgetItem, QApplication
from .qt_base_widget_component import QtBaseWidgetComponent
from .styling import q_color_from_color, q_font_from_font

from ...components.widget_component import AbstractTkWidgetComponent
from ...layout.geometry import Rect, Size, Pos


class QtWidgetComponent(QtBaseWidgetComponent, AbstractTkWidgetComponent):
    """ A Qt4 implementation of WidgetComponent.

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

    def create(self, parent):
        """ Creates the underlying Qt widget. As necessary, subclasses
        should reimplement this method to create different types of
        widgets.

        """
        self.widget = QFrame(parent)

    def initialize(self):
        """ Initializes the attributes of the the Qt widget.

        """
        super(QtWidgetComponent, self).initialize()
        shell = self.shell_obj
        self.set_enabled(shell.enabled)
        if shell.bgcolor:
            self.set_bgcolor(shell.bgcolor)
        if shell.fgcolor:
            self.set_fgcolor(shell.fgcolor)
        if shell.font:
            self.set_font(shell.font)

    def enable_updates(self):
        """ Enable rendering updates for the underlying Wx widget.

        """
        # Freezing updates on a top-level window seems to cause 
        # flicker on OSX when the updates are reenabled. In this 
        # case, just freeze the children instead.
        if self.widget.isWindow():
            for child in self.shell_obj.children:
                child.enable_updates()
        self.widget.setUpdatesEnabled(True)
    
    def disable_updates(self):
        """ Disable rendering updates for the underlying Qt widget.

        """
        # Freezing updates on a top-level window seems to cause 
        # flicker on OSX when the updates are reenabled. In this 
        # case, just freeze the children instead.
        if self.widget.isWindow():
            for child in self.shell_obj.children:
                child.disable_updates()
        else:
            self.widget.setUpdatesEnabled(False)

    def set_visible(self, visible):
        """ Show or hide the widget.

        """
        self.widget.setVisible(visible)

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
        return Size(size_hint.width(), size_hint.height())

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
        return Rect(geo.x(), geo.y(), geo.width(), geo.height())

    def set_layout_geometry(self, rect):
        """ Sets the layout geometry of the internal widget to the 
        given x, y, width, and height values. The parameters passed
        are equivalent semantics to layout_geometry().

        """
        rect = QRect(*rect)
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
        return Rect(geom.x(), geom.y(), geom.width(), geom.height())

    def set_geometry(self, rect):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        self.widget.setGeometry(*rect)

    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        min_size = self.widget.minimumSize()
        return Size(min_size.width(), min_size.height())

    def set_min_size(self, size):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        self.widget.setMinimumSize(*size)

    def max_size(self):
        """ Returns the hard maximum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized larger than this value

        """
        max_size = self.widget.maximumSize()
        return Size(max_size.width(), max_size.height())

    def set_max_size(self, size):
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
        max_width, max_height = size
        max_width = min(max_width, 16777215)
        max_height = min(max_height, 16777215)
        self.widget.setMaximumSize(max_width, max_height)

    def size(self):
        """ Returns the size of the internal toolkit widget, ignoring any
        windowing decorations, as a (width, height) tuple of integers.

        """
        size = self.widget.size()
        return Size(size.width(), size.height())
                
    def resize(self, size):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        self.widget.resize(*size)

    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers, including any windowing decorations. 
        The coordinates should be relative to the origin of the widget's 
        parent, or to the screen if the widget is toplevel.

        """
        pos = self.widget.pos()
        return Pos(pos.x(), pos.y())
            
    def move(self, pos):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        self.widget.move(*pos)

    def shell_enabled_changed(self, enabled):
        """ The change handler for the 'enabled' attribute on the shell
        object.

        """
        self.set_enabled(enabled)

    def shell_bgcolor_changed(self, color):
        """ The change handler for the 'bgcolor' attribute on the shell
        object. Sets the background color of the internal widget to the 
        given color.
        
        """
        self.set_bgcolor(color)
    
    def shell_fgcolor_changed(self, color):
        """ The change handler for the 'fgcolor' attribute on the shell
        object. Sets the foreground color of the internal widget to the 
        given color.

        """
        self.set_fgcolor(color)

    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the shell 
        object. Sets the font of the internal widget to the given font.

        """
        self.set_font(font)

    def set_enabled(self, enabled):
        """ Enable or disable the widget.

        """
        self.widget.setEnabled(enabled)

    def set_bgcolor(self, color):
        """ Sets the background color of the widget to an appropriate
        QColor given the provided Enaml Color object.

        """
        widget = self.widget
        role = widget.backgroundRole()
        if not color:
            palette = QApplication.instance().palette(widget)
            qcolor = palette.color(role)
            # On OSX, the default color is rendered *slightly* off
            # so a simple workaround is to tell the widget not to
            # auto fill the background.
            widget.setAutoFillBackground(False)
        else:
            qcolor = q_color_from_color(color)
            # When not using qt style sheets to set the background
            # color, we need to tell the widget to auto fill the 
            # background or the bgcolor won't render at all.
            widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

    def set_fgcolor(self, color):
        """ Sets the foreground color of the widget to an appropriate
        QColor given the provided Enaml Color object.

        """
        widget = self.widget
        role = widget.foregroundRole()
        if not color:
            palette = QApplication.instance().palette(widget)
            qcolor = palette.color(role)
        else:
            qcolor = q_color_from_color(color)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

    def set_font(self, font):
        """ Sets the font of the widget to an appropriate QFont given 
        the provided Enaml Font object.

        """
        q_font = q_font_from_font(font)
        self.widget.setFont(q_font)

