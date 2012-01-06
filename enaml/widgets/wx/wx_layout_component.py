#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_component import WXComponent

from ..layout_component import AbstractTkLayoutComponent


class WXLayoutComponent(WXComponent, AbstractTkLayoutComponent):
    """ A wxPython implementation of LayoutComponent.

    """
    #--------------------------------------------------------------------------
    # Abstract Implementation
    #--------------------------------------------------------------------------
    def size(self):
        """ Returns the size of the internal toolkit widget, ignoring any
        windowing decorations, as a (width, height) tuple of integers.

        """
        return self._size(self.widget)

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, ignoring
        any windowing decorations. This value is used by the layout 
        manager to determine how much space to allocate the widget.

        """
        return self._size_hint(self.widget)

    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        self._resize(self.widget, width, height)

    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        return self._min_size(self.widget)

    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        self._set_min_size(self.widget, min_width, min_height)

    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers, including any windowing decorations. 
        The coordinates should be relative to the origin of the widget's 
        parent, or to the screen if the widget is toplevel.

        """
        return self._pos(self.widget)

    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        self._move(self.widget, x, y)

    def frame_geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, including any windowing
        decorations.

        """
        return self._frame_geometry(self.widget)

    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, ignoring any windowing
        decorations.

        """
        return self._geometry(self.widget)

    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        self._set_geometry(self.widget, x, y, width, height)

    #--------------------------------------------------------------------------
    # Indirection getters and setters 
    #--------------------------------------------------------------------------
    
    # These indirection methods allow subclasses to not need to repeat
    # code when they need to maintain two separate internal widgets
    # (See WXWindow for an example). Instead they can just call these
    # methods.

    def _size(self, widget):
        """ Returns the size of the given widget. See also 'size()'.

        """
        return widget.GetClientSizeTuple()

    def _size_hint(self, widget):
        """ Returns the size hint of the given widget. See also 
        'size_hint()'.

        """
        return widget.GetBestSizeTuple()

    def _resize(self, widget, width, height):
        """ Resizes the given widget. See also 'resize(width, height)'

        """
        # SetClientSize completely breaks down on Windows, so it seems 
        # there is no way to reliably set the client size. Instead we
        # just set the frame size and hope for the best.
        widget.SetSize((width, height))

    def _min_size(self, widget):
        """ Returns the minimum size of the widget. See also
        'min_size()'.

        """
        # Wx really needs a GetMinClientSize function...
        return tuple(widget.GetMinSize())

    def _set_min_size(self, widget, min_width, min_height):
        """ Sets the minimum size of the given widget. See also
        'set_min_size(min_width, min_height)'.

        """
        # Wx really needs a SetMinClientSize function...
        widget_width, widget_height = widget.GetSizeTuple()
        client_width, client_height = widget.GetClientSizeTuple() 
        min_width = min_width + (widget_width - client_width)
        min_height = min_height + (widget_height - client_height)
        widget.SetMinSize((min_width, min_height))
        new_size = (max(widget_width, min_width), max(widget_height, min_height))
        if new_size != (widget_width, widget_height):
            widget.SetSize(new_size)

    def _pos(self, widget):
        """ Returns the position of the given widget. See also 'pos()'.

        """
        return widget.GetPositionTuple()

    def _move(self, widget, x, y):
        """ Moves the widget to the given position. See also 'move(x, y)'.

        """
        widget.Move((x, y))

    def _frame_geometry(self, widget):
        """ Returns the frame geometry of the given widget. See also
        'frame_geometry()'.

        """
        return widget.GetRect().asTuple()

    def _geometry(self, widget):
        """ Returns the geometry of the given widget. See also
        'geometry()'.

        """
        # wx widget.GetClientRect() doesn't seem to be what we want.
        # ofter, GetRect() and GetClientRect() are the same, but when
        # they aren't GetRect() does the right thing. This is probably
        # because of asymmetry between GetClientRect and SetDimensions. 
        # Given that, the existing examples have been tested side by 
        # side with Qt on Windows, and these current geometry handlers 
        # "do the right thing" in most cases, plus or minus a pixel or
        # two difference.
        return widget.GetRect().asTuple()

    def _set_geometry(self, widget, x, y, width, height):
        """ Sets the geometry of the given widget. See also
        'set_geometry(x, y, width, height)'.

        """
        # wx doesn't seem to have a SetClientDimensions function
        # or anything similar. SetClientRect *does not* do the right
        # thing. This SetDimensions *seems* to do the correct thing
        # but I'm skeptical that it won't break down in certain 
        # cirumstances and do the wrong thing wrt to window decorations.
        widget.SetDimensions(x, y, width, height)

