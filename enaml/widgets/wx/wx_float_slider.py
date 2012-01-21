#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_slider import WXSlider

from ..float_slider import AbstractTkFloatSlider


class WXFloatSlider(WXSlider, AbstractTkFloatSlider):
    """ A wxPython implementation of FloatSlider.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------

    def initialize(self):
        """ Initializes the attributes of the toolkit widget.

        """
        # Setting double buffered reduces flicker on Windows
        self.widget.SetDoubleBuffered(True)
        shell = self.shell_obj
        shell._down = False
        self.set_precision(shell.precision)
        super(WXSlider, self).initialize()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------

    def shell_precision_changed(self, precision):
        """ The change handler for the 'precision' attribute on the shell
        object.
        
        """
        self.set_precision(precision)

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_slider_moved(self, event):
        """ The event handler for a slider drag event.

        """
        shell = self.shell_obj
        value = self.int_to_float(self.widget.GetValue())

        # Update the value only if tracking is turned on.
        if shell.tracking:
            shell.value = value
        
        # Since this event is only fired when the drag handle is 
        # moved with the mouse, it's safe to fire the move event
        # with no further checks.
        shell.moved(value)

        event.Skip()

    def _on_slider_keyed(self, event):
        """ The event handler for the user changing the value of the 
        slider through a key.

        """
        self.shell_obj.value = self.int_to_float(self.widget.GetValue())
        event.Skip()

    def _on_left_down(self, event):
        """ The event handler for the left mouse button being pressed.
        This estimates the position of the drag handle and then checks 
        if the mouse was pressed over it and then fires the `pressed` 
        event and sets the `down` attribute.

        """
        # Wx does not provide an event for detecting a mouse press
        # on the drag handle. So we have to estimate it by doing a
        # bit of geometry. This is not very accurate but probably
        # sufficient for most use cases.
        shell = self.shell_obj
        widget = self.widget
        mouse_position = event.GetPosition()
        slider_position = widget.GetValue()
        thumb = widget.GetThumbLength() / 2.0
        width, height = widget.GetClientSizeTuple()

        if widget.HasFlag(wx.SL_VERTICAL):
            position = mouse_position[1] / float(height)
        else:
            position = mouse_position[0] / float(width)

        slider_length = float(widget.GetMax() - widget.GetMin()) + 1.0
        minimum = (slider_position - thumb) / slider_length
        maximum = (slider_position + thumb) / slider_length

        hit = minimum <= position <= maximum

        if hit:
            shell._down = True
            shell.pressed()
        
        event.Skip()

    def _on_thumb_released(self, event):
        """ The event handler for drag handle being released. It
        updates the value in the shell and fires the appropriate
        events.

        """
        shell = self.shell_obj
        value = self.int_to_float(self.widget.GetValue())
        shell.value = value
        if shell._down:
            shell._down = False
            shell.released()
        event.Skip()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_precision(self, precision):
        """ Set the precision attribute in the Qt widget.

        """
        self.widget.SetRange(0, precision)

    def set_range(self, minimum, maximum):
        """ Set the range of the slider widget.

        Overridden to ignore the float values. The Qt widget knows nothing about
        them.

        """
        pass

    def set_position(self, value):
        """ Validate the position value.

        """
        self.widget.SetValue(self.float_to_int(value))

    def float_to_int(self, value):
        """ Convert a float value to an int value.

        """
        shell = self.shell_obj
        u = (value - shell.minimum) / (shell.maximum - shell.minimum)
        i = int(round(u * shell.precision))
        return i

    def int_to_float(self, value):
        """ Convert an int value to a float value.

        """
        shell = self.shell_obj
        u = float(value) / shell.precision
        x = u * shell.maximum + (1.0-u) * shell.minimum
        return x


