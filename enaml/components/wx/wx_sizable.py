#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..sizable import AbstractTkSizable


class WXSizable(AbstractTkSizable):
    """ A Wx implementation of Sizable.

    """
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, ignoring
        any windowing decorations. This value is used by the layout 
        manager to determine how much space to allocate the widget.

        """
        return self.widget.GetBestSizeTuple()

    def layout_geometry(self):
        """ Returns the (x, y, width, height) to of layout geometry
        info for the internal toolkit widget. This should ignore any
        windowing decorations, and may be different than the value
        returned by geometry() if the widget's effective layout rect
        is different from its paintable rect.

        """
        return self.geometry()

    def set_layout_geometry(self, x, y, width, height):
        """ Sets the layout geometry of the internal widget to the 
        given x, y, width, and height values. The parameters passed
        are equivalent semantics to layout_geometry().

        """
        self.set_geometry(x, y, width, height)

    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, ignoring any windowing
        decorations.

        """
        # wx widget.GetClientRect() doesn't seem to be what we want.
        # Often, GetRect() and GetClientRect() are the same, but when
        # they aren't, GetRect() does the right thing. This is probably
        # because of asymmetry between GetClientRect and SetDimensions. 
        # Given that, the existing examples have been tested side by 
        # side with Qt on Windows, and these current geometry handlers 
        # "do the right thing" in most cases, plus or minus a pixel or
        # two difference.
        return self.widget.GetRect().asTuple()

    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        # wx doesn't seem to have a SetClientDimensions function
        # or anything similar. SetClientRect *does not* do the right
        # thing. This SetDimensions *seems* to do the correct thing
        # but I'm skeptical that it won't break down in certain 
        # cirumstances and do the wrong thing wrt to window decorations.
        self.widget.SetDimensions(x, y, width, height)

    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        widget = self.widget
        widget_width, widget_height = widget.GetSizeTuple()
        client_width, client_height = widget.GetClientSizeTuple()
        min_width, min_height = tuple(widget.GetMinSize())
        min_width = min_width - (widget_width - client_width)
        min_height = min_height - (widget_height - client_height)
        return (min_width, min_height)

    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        # Wx is lacking a SetMinClientSize function, so we fake it.
        widget = self.widget
        widget_width, widget_height = widget.GetSizeTuple()
        client_width, client_height = widget.GetClientSizeTuple()
        delta_width = widget_width - client_width
        delta_height = widget_height - client_height
        min_width = min_width + delta_width
        min_height = min_height + delta_height

        # Wx won't automatically reset the max size if the min size
        # is larger. Ugh....
        max_width, max_height = self.max_size()
        max_width = max(min_width, max_width + delta_width)
        max_height = max(min_height, max_height + delta_height)
        self.widget.SetMaxSize((max_width, max_height))

        widget.SetMinSize((min_width, min_height))

        # If the min size is now smaller that the existing size, resize
        # the widget to meet the min size.
        #
        # XXX this is a bit wrong, it should only resize the offending
        # dimension.
        new_width = max(widget_width, min_width)
        new_height = max(widget_height, min_height)
        new_size = (new_width, new_height)
        if new_size != (widget_width, widget_height):
            widget.SetSize(new_size)

    def max_size(self):
        """ Returns the hard maximum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized larger than this value

        """
        # Wx is lacking a MaxClientSize function, so we fake it.
        widget = self.widget
        widget_width, widget_height = widget.GetSizeTuple()
        client_width, client_height = widget.GetClientSizeTuple()
        max_width, max_height = tuple(widget.GetMaxSize())
        max_width = max_width - (widget_width - client_width)
        max_height = max_height - (widget_height - client_height)
        return (max_width, max_height)

    def set_max_size(self, max_width, max_height):
        """ Set the hard maximum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        larger than this value.

        """
        # Wx is lacking a SetMaxClientSize function and at the moment, 
        # it's uncertain what the maximum allowable size is on wx. For 
        # now, we just fake computation and use the Qt limits.
        widget = self.widget
        widget_width, widget_height = widget.GetSizeTuple()
        client_width, client_height = widget.GetClientSizeTuple()
        delta_width = widget_width - client_width
        delta_height = widget_height - client_height 
        max_width = max_width + delta_width
        max_height = max_height + delta_height
        max_width = min(max_width, 16777215)
        max_height = min(max_height, 16777215)

        # Wx won't automatically reset the min size if the max size
        # is smaller. Ugh....
        min_width, min_height = self.min_size()
        min_width = min(min_width + delta_width, max_width)
        min_height = min(min_height + delta_height, max_height)
        self.widget.SetMinSize((min_width, min_height))

        self.widget.SetMaxSize((max_width, max_height))

        # If the max size is now larger that the existing size, resize
        # the widget to meet the max size.
        #
        # XXX this is a bit wrong, it should only resize the offending
        # dimension.
        new_width = min(widget_width, max_width)
        new_height = min(widget_height, max_height)
        new_size = (new_width, new_height)
        if new_size != (widget_width, widget_height):
            widget.SetSize(new_size)

    def size(self):
        """ Returns the size of the internal toolkit widget, ignoring any
        windowing decorations, as a (width, height) tuple of integers.

        """
        return self.widget.GetClientSizeTuple()
                
    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        # SetClientSize completely breaks down on Windows, so we fake 
        # it and hope for the best.
        widget = self.widget
        widget_width, widget_height = widget.GetSizeTuple()
        client_width, client_height = widget.GetClientSizeTuple() 
        width = width + (widget_width - client_width)
        height = height + (widget_height - client_height)
        self.widget.SetSize((width, height))

    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers, including any windowing decorations. 
        The coordinates should be relative to the origin of the widget's 
        parent, or to the screen if the widget is toplevel.

        """
        return self.widget.GetPositionTuple()
            
    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        self.widget.Move((x, y))

