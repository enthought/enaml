#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_base_widget_component import WXBaseWidgetComponent
from .styling import wx_color_from_color, wx_font_from_font

from ...components.widget_component import AbstractTkWidgetComponent
from ...layout.geometry import Rect, Size, Pos


#: An event that is emitted when the minimum size is set on a widget. 
#: This is required by the WXMainWindowSizer to know when to resize
#: the frame if the central widget's min size has changed.
wxMinSizeChanged, EVT_MIN_SIZE = wx.lib.newevent.NewEvent()


class WXWidgetComponent(WXBaseWidgetComponent, AbstractTkWidgetComponent):
    """ A Wx implementation of WidgetComponent.

    """
    def create(self, parent):
        """ Creates the underlying Wx widget. As necessary, subclasses
        should reimplement this method to create different types of
        widgets.

        """
        self.widget = wx.Panel(parent)

    def initialize(self):
        """ Initializes the attributes of the the Wx widget.

        """
        super(WXWidgetComponent, self).initialize()
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
        widget = self.widget
        if widget:
            if widget.IsFrozen():
                widget.Thaw()
    
    def disable_updates(self):
        """ Disable rendering updates for the underlying Wx widget.

        """
        widget = self.widget
        if widget:
            if not widget.IsFrozen():
                widget.Freeze()

    def set_visible(self, visible):
        """ Show or hide the widget.

        """
        self.widget.Show(visible)

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, ignoring
        any windowing decorations. This value is used by the layout 
        manager to determine how much space to allocate the widget.

        """
        return Size(*self.widget.GetBestSizeTuple())

    def layout_geometry(self):
        """ Returns the (x, y, width, height) to of layout geometry
        info for the internal toolkit widget. This should ignore any
        windowing decorations, and may be different than the value
        returned by geometry() if the widget's effective layout rect
        is different from its paintable rect.

        """
        return self.geometry()

    def set_layout_geometry(self, rect):
        """ Sets the layout geometry of the internal widget to the 
        given x, y, width, and height values. The parameters passed
        are equivalent semantics to layout_geometry().

        """
        self.set_geometry(rect)

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
        return Rect(*self.widget.GetRect().asTuple())

    def set_geometry(self, rect):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        # wx doesn't seem to have a SetClientDimensions function
        # or anything similar. SetClientRect *does not* do the right
        # thing. This SetDimensions *seems* to do the correct thing
        # but I'm skeptical that it won't break down in certain 
        # cirumstances and do the wrong thing wrt to window decorations.
        self.widget.SetDimensions(*rect)

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
        return Size(min_width, min_height)

    def set_min_size(self, size):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        # Wx is lacking a SetMinClientSize function, so we fake it.
        widget = self.widget
        min_width, min_height = size
        widget_width, widget_height = widget.GetSizeTuple()
        client_width, client_height = widget.GetClientSizeTuple()
        delta_width = widget_width - client_width
        delta_height = widget_height - client_height
        min_width = min_width + delta_width
        min_height = min_height + delta_height

        # Wx won't automatically reset the max size if the min size
        # is larger, ugh. Additionally, we don't want to update the
        # max size if it's < 0 since that indicates the max size is
        # not bounded. 
        max_width, max_height = self.max_size()
        if max_width >= 0 and max_height >= 0:
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

        # We create and emit a min size event so that if this widget
        # is the central widget in a MainWindow, the sizer for that
        # window can properly update the minimum size of the frame.
        evt = wxMinSizeChanged()
        wx.PostEvent(widget, evt)

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
        return Size(max_width, max_height)

    def set_max_size(self, size):
        """ Set the hard maximum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        larger than this value.

        """
        # Wx is lacking a SetMaxClientSize function and at the moment, 
        # it's uncertain what the maximum allowable size is on wx. For 
        # now, we just fake computation and use the Qt limits.
        widget = self.widget
        max_width, max_height = size
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
        return Size(*self.widget.GetClientSizeTuple())
                
    def resize(self, size):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        # SetClientSize completely breaks down on Windows, so we fake 
        # it and hope for the best.
        widget = self.widget
        width, height = size
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
        return Pos(*self.widget.GetPositionTuple())
            
    def move(self, pos):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        self.widget.Move(pos)

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
        self.widget.Enable(enabled)

    def set_bgcolor(self, color):
        """ Sets the background color of the widget to an appropriate
        wxColor given the provided Enaml Color object.

        """
        wx_color = wx_color_from_color(color)
        self.widget.SetBackgroundColour(wx_color)

    def set_fgcolor(self, color):
        """ Sets the foreground color of the widget to an appropriate
        wxColor given the provided Enaml Color object.

        """
        wx_color = wx_color_from_color(color)
        self.widget.SetForegroundColour(wx_color)

    def set_font(self, font):
        """ Sets the font of the widget to an appropriate QFont given 
        the provided Enaml Font object.

        """
        # There's no such thing as a NullFont on wx, so if the font is
        # equivalent to the Enaml default font, and we haven't yet changed 
        # the font for this instance, then we don't change it. Otherwise
        # the fonts won't be equivalelnt to the default.
        if not font and self._has_default_wx_font:
            return

        wx_font = wx_font_from_font(font)
        self.widget.SetFont(wx_font)
        self._has_default_wx_font = False

