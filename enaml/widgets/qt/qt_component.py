#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_base_component import QtBaseComponent

from ..component import AbstractTkComponent


class QtComponent(QtBaseComponent, AbstractTkComponent):
    """ A Qt4 implementation of Component.

    """
    #: A reference to the Qt layout item used determine various aspects
    #: of the layout geometry of the widget.
    _layout_item = None

    #: A tuple of margins which are the offsets from the widget rect
    #: to the widget layout rect
    _layout_margins = None

    #: A tuple of layout margins for the parent of the instances 
    #: toolkit widget
    _parent_margins = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initializes the attributes of the Qt widget.

        """
        super(QtComponent, self).initialize()
        self._layout_item = QtGui.QWidgetItem(self.widget)
        self._reset_layout_margins()
        
    #--------------------------------------------------------------------------
    # Abstract Implementation
    #--------------------------------------------------------------------------
    def size(self):
        """ Returns the size of the internal toolkit widget, ignoring any
        windowing decorations, as a (width, height) tuple of integers.

        """
        geom = self._layout_item.geometry()
        return (geom.width(), geom.height())

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, ignoring
        any windowing decorations. This value is used by the layout 
        manager to determine how much space to allocate the widget.

        """
        size_hint = self._layout_item.sizeHint()
        return (size_hint.width(), size_hint.height())

    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        dx, dy, dr, db = self._layout_margins
        self.widget.resize(width+dx+dr, height+dy+db)
    
    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        widget = self.widget
        return (widget.minimumWidth(), widget.minimumHeight())

    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        dx, dy, dr, db = self._layout_margins
        self.widget.setMinimumSize(min_width+dx+dr, min_height+dy+db)

    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers, including any windowing decorations. 
        The coordinates should be relative to the origin of the widget's 
        parent, or to the screen if the widget is toplevel.

        """
        widget = self.widget
        return (widget.x(), widget.y())

    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        self.widget.move(x, y)

    def frame_geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, including any windowing
        decorations.

        """
        geo = self.widget.frameGeometry()
        return (geo.x(), geo.y(), geo.width(), geo.height())

    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, ignoring any windowing
        decorations.

        """
        pdx, pdy, pdr, pdb = self._parent_margins
        geom = self._layout_item.geometry()
        return (geom.x()-pdx, geom.y()-pdy, geom.width(), geom.height())

    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        dx, dy, dr, db = self._layout_margins
        pdx, pdy, pdr, pdb = self._parent_margins
        self.widget.setGeometry(x-dx+pdx, y-dy+pdy, width+dr+dx, height+db+dy)

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def _get_layout_margins(self, widget):
        """ Compute the size of the margins between the layout rectangle 
        and the widget drawing rectangle.

        """
        layout_geom = QtGui.QWidgetItem(widget).geometry()
        widget_geom = widget.geometry()
        margins = (layout_geom.x() - widget_geom.x(),
                   layout_geom.y() - widget_geom.y(),
                   widget_geom.right() - layout_geom.right(),
                   widget_geom.bottom() - layout_geom.bottom())
        return margins

    def _reset_layout_margins(self):
        """ Reset the layout margins for this widget.

        """
        self._layout_margins = self._get_layout_margins(self.widget)
        parent = self.widget.parent()
        if parent is not None:
            self._parent_margins = self._get_layout_margins(parent)
        else:
            self._parent_margins = (0, 0, 0, 0)

