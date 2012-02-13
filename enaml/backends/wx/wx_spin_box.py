#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_control import WXControl

from ..spin_box import AbstractTkSpinBox

from ...converters import IntConverter


#: The changed event for the custom spin ctrl.
CustomSpinCtrlEvent, EVT_CUSTOM_SPINCTRL = wx.lib.newevent.NewEvent()


class CustomSpinCtrl(wx.SpinCtrl):
    """ A custom wx spin control that acts more like QSpinBox.

    The standard wx.SpinCtrl doesn't support too many features, and
    the ones it does support are (like wrapping) are limited. So,
    this custom control hard codes the internal range to the maximum
    range of the wx.SpinCtrl and implements wrapping manually.

    For changed events, users should bind to EVT_CUSTOM_SPINCTRL
    rather than EVT_SPINCTRL.

    See the method docstrings for supported functionality.
    
    This custom control does not support the tracking mode that is
    available in the Qt version. It's infeasible to implement this
    using a subclass of wx.SpinCtrl. Implementing this would
    require create a custom wx.PyControl that combines a wx.TextCtrl
    and wx.SpinButton into a single control.

    """
    #: The text in the control may be acceptable
    INTERMEDIATE = 1
    
    #: The text in the control is a valid value
    ACCEPTABLE = 2

    def __init__(self, parent, low=0, high=100, step=1, converter=None, wrap=False):
        """ CustomSpinCtrl constructor.

        Arguments
        ---------
        parent : wxWindow
            The parent of the spin ctrl.

        low : int, optional
            The minimum value of spin ctrl. Defaults to 0.

        high : int, optional
            The maximum value of the spin ctrl. Defaults to 100.

        step : int, optional
            The step amount to use for the spin ctrl. Defaults to 1.

        converter : Instance(Converter), optional
            A converter to use to convert to and from string display
            values and the internal integer value of the control.
            Defaults to IntConverter().

        wrap : bool, optional
            A flag indicating whether the spin ctrl should wrap
            at the ends.

        """
        # The max range of the wx.SpinCtrl is the range of a signed
        # 32bit integer. We don't care about wx's internal value of
        # the control, since we maintain our own internal counter.
        # and because the internal value of the widget gets reset to
        # the minimum of the range whenever SetValueString is called.
        self._hard_min = -(1 << 31)
        self._hard_max = (1 << 31) - 1
        self._internal_value = low
        self._low = low
        self._high = high
        self._step = step
        self._converter = converter or IntConverter()
        self._value_string = self._converter.to_component(low)
        self._wrap = wrap

        # Stores whether spin-up or spin-down was pressed.
        self._spin_state = None

        super(CustomSpinCtrl, self).__init__(parent)
        super(CustomSpinCtrl, self).SetRange(self._hard_min, self._hard_max)

        # Setting the spin control to process the enter key removes
        # its processing of the Tab key. This is desired for two reasons:
        # 1) It is consistent with the Qt version of the control.
        # 2) The default tab processing is kinda wacky in that when 
        #    tab is pressed, it emits a text event with the string
        #    representation of the integer value of the control,
        #    regardless of the value of the user supplied string.
        #    This is definitely not correct and so processing on 
        #    Enter allows us to avoid the issue entirely.
        self.WindowStyle |= wx.TE_PROCESS_ENTER

        self.Bind(wx.EVT_SPIN_UP, self.OnSpinUp)
        self.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDown)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinCtrl)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterPressed)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnEnterPressed(self, event):
        """ The event handler for an enter key press. It forces an 
        interpretation of the current text control value.

        """
        self.InterpretText()

    def OnKillFocus(self, event):
        """ Handles evaluating the text in the control when the control 
        loses focus. 

        """
        event.Skip()
        # The spin control doesn't emit a spin event when losing focus
        # to process typed input change unless it results in a different
        # value, so we have to handle it manually and update the control
        # again after the event. It must be invoked on a CallAfter or it 
        # doesn't work properly. The lambda avoids a DeadObjectError if 
        # the app is exited before the callback executes.
        wx.CallAfter(lambda: self.InterpretText() if self else None)

    def OnText(self, event):
        """ Handles the text event of the spin control to store away the
        user typed text for later conversion.

        """
        # Do not be tempted to try to implement the 'tracking' feature
        # by adding logic to this method. Wx emits this event at weird
        # times such as ctrl-a select all as well as when SetValueString
        # is called. Granted, this can be avoided with a recursion guard,
        # however, there is no way to get/set the caret position on the
        # control and every call to SetValueString resets the caret 
        # position to Zero. So, there is really no possible way to 
        # implement 'tracking' without creating an entirely new custom
        # control. So for now, the wx backend just lacks that feature.
        self._value_string = event.GetString()

    def OnSpinUp(self, event):
        """ The event handler for the spin up event. We veto the spin
        event to prevent the control from changing it's internal value.
        Instead, we maintain complete control of the value.

        """
        event.Veto()
        self._spin_state = 'up'
        self.OnSpinCtrl(event)
        self._spin_state = None

    def OnSpinDown(self, event):
        """ The event handler for the spin down event. We veto the spin
        event to prevent the control from changing it's internal value.
        Instead, we maintain complete control of the value.

        """
        event.Veto()
        self._spin_state = 'down'
        self.OnSpinCtrl(event)
        self._spin_state = None

    def OnSpinCtrl(self, event):
        """ Handles the spin control being changed by user interaction.
        All of the manual stepping and wrapping logic is computed by
        this method.

        """
        last = self._internal_value
        low = self._low
        high = self._high
        step = self._step
        wrap = self._wrap
        spin_state = self._spin_state

        if spin_state == 'down':
            if last == low:
                if wrap:
                    computed = high
                else:
                    computed = low
            else:
                computed = last - step
                if computed < low:
                    computed = low
            self.SetValue(computed)
        elif spin_state == 'up':
            if last == high:
                if wrap:
                    computed = low
                else:
                    computed = high
            else:
                computed = last + step
                if computed > high:
                    computed = high
            self.SetValue(computed)
        else:
            # A suprious spin event generated by wx when the widget loses 
            # focus. We can safetly ignore it.
            pass

    #--------------------------------------------------------------------------
    # Getters/Setters 
    #--------------------------------------------------------------------------
    def GetLow(self):
        """ Returns the minimum value of the control.

        """
        return self._low

    def GetMin(self):
        """ Equivalent to GetLow().

        """
        return self._low

    def SetLow(self, low):
        """ Sets the minimum value of the control and changes the
        value to the min if the current value would be out of range.

        """
        if low < self._hard_min:
            raise ValueError('%s too low for CustomSpinCtrl.' % low)
        self._low = low
        if self.GetValue() < low:
            self.SetValue(low)

    def GetHigh(self):
        """ Returns the maximum value of the control.

        """
        return self._high

    def GetMax(self):
        """ Equivalent to GetHigh().

        """
        return self._high

    def SetHigh(self, high):
        """ Sets the maximum value of the control and changes the
        value to the max if the current value would be out of range.

        """
        if high > self._hard_max:
            raise ValueError('%s too high for CustomSpinCtrl.' % high)
        self._high = high
        if self.GetValue() > high:
            self.SetValue(high)

    def SetRange(self, low, high):
        """ Sets the low and high values of the control.

        """
        self.SetLow(low)
        self.SetHigh(high)

    def GetStep(self):
        """ Returns the step size of the control.

        """
        return self._step

    def SetStep(self, step):
        """ Sets the step size of the control.

        """
        self._step = step

    def GetConverter(self):
        """ Returns the converter in use for the control.

        """
        return self._converter
    
    def SetConverter(self, converter):
        """ Sets the converter in use for the control.

        """
        self._converter = converter
        self.InterpretText()

    def GetWrap(self):
        """ Gets the wrap flag of the control.

        """
        return self._wrap

    def SetWrap(self, wrap):
        """ Sets the wrap flag of the control.

        """
        self._wrap = wrap

    def GetValue(self):
        """ Returns the internal integer value of the control.

        """
        return self._internal_value

    def SetValue(self, value):
        """ Sets the value of the control to the given value, provided
        that the value is within the range of the control. If the
        given value is within range, and is different from the current
        value of the control, an EVT_CUSTOM_SPINCTRL will be emitted.

        """
        different = False
        if self._low <= value <= self._high:
            different = (self._internal_value != value)
            self._internal_value = value

        # Always set the value string, just to be overly 
        # safe that we don't fall out of sync.
        self._value_string = self.TextFromValue(self._internal_value)
        self.SetValueString(self._value_string)

        if different:
            evt = CustomSpinCtrlEvent()
            wx.PostEvent(self, evt)

    #--------------------------------------------------------------------------
    # Support Methods 
    #--------------------------------------------------------------------------
    def InterpretText(self):
        """ Interprets the user supplied text and updates the control. 

        """
        text = self._value_string
        valid = self.Validate(text)
        if valid == self.ACCEPTABLE:
            value = self.ValueFromText(text)
            self.SetValue(value)
        else:
            # If the text does not validate, use the current value.
            self.SetValue(self._internal_value)

    def TextFromValue(self, value):
        """ Converts the given integer to a string for display using
        the user supplied converter object. 

        If the conversion fails due to the converter raising a ValueError
        then simple str(...) conversion is used.

        """
        try:
            text = self._converter.to_component(value)
        except ValueError:
            text = str(value)
        return text

    def ValueFromText(self, text):
        """ Converts the user typed string into an integer for the
        control using the user supplied converter.

        """
        # This will only be called if the validate method has returned 
        # ACCEPTABLE, so we can assume that calling the converter again 
        # will not raise an error. Further, we don't worry too much about 
        # calling the converter twice since it should be a relatively 
        # cheap operation to convert a string to some int. If it's not, 
        # then a given converter can implement its own internal caching 
        # to speed things up.
        return self._converter.from_component(text)

    def Validate(self, text):
        """ Validates whether or not the given text can be converted
        to a valid integer.

        """
        try:
            val = self._converter.from_component(text)
        except ValueError:
            res = self.INTERMEDIATE
        else:
            if self._low <= val <= self._high:
                res = self.ACCEPTABLE
            else:
                res = self.INTERMEDIATE
        return res


class WXSpinBox(WXControl, AbstractTkSpinBox):
    """ A wxPython implementation of SpinBox.

    WXSpinBox uses a custom subclass of wx.SpinCtrl that behaves more
    like Qt's QSpinBox.

    """
    def create(self, parent):
        """ Creates the underlying custom spin control.

        """
        self.widget = CustomSpinCtrl(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        # Note: Don't set the widget to double buffered, it causes 
        # rendering problems on Windows where the spin buttons fail
        # to paint reliably.
        super(WXSpinBox, self).initialize()
        shell = self.shell_obj
        self.set_spin_low(shell.low)
        self.set_spin_high(shell.high)
        self.set_spin_step(shell.step)
        self.set_spin_converter(shell.converter)
        self.set_spin_wrap(shell.wrap)
        self.set_spin_value(shell.value)

    def bind(self):
        """ Binds the event handlers for the spin control.

        """
        super(WXSpinBox, self).bind()
        self.widget.Bind(EVT_CUSTOM_SPINCTRL, self.on_custom_spin_ctrl)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute.

        """
        self.set_spin_value(value)

    def shell_low_changed(self, low):
        """ The change handler for the 'low' attribute.

        """
        self.set_spin_low(low)

    def shell_high_changed(self, high):
        """ The change handler for the 'high' attribute.

        """
        self.set_spin_high(high)

    def shell_step_changed(self, step):
        """ The change handler for the 'step' attribute.

        """
        self.set_spin_step(step)

    def shell_converter_changed(self, converter):
        """ The change handler for the 'converter' attribute.

        """
        self.set_spin_converter(converter)

    def shell_wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute.

        """
        self.set_spin_wrap(wrap)

    def shell_tracking_changed(self, tracking):
        """ The change handler for the 'tracking' attribute of the shell
        object. The wx implementation does not support keyboard tracking.

        """
        pass

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def on_custom_spin_ctrl(self, event):
        """ The event handler for the widget's spin event.

        """
        self.shell_obj.value = self.widget.GetValue()
        event.Skip()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_spin_value(self, value):
        """ Updates the widget with the given value.

        """
        self.widget.SetValue(value)

    def set_spin_low(self, low):
        """ Updates the low limit of the spin box.

        """
        self.widget.SetLow(low)

    def set_spin_high(self, high):
        """ Updates the high limit of the spin box.

        """
        self.widget.SetHigh(high)

    def set_spin_step(self, step):
        """ Updates the step of the spin box.

        """
        self.widget.SetStep(step)

    def set_spin_converter(self, converter):
        """ Updates the 'to_string' and 'from_string' functions of the
        spin box. Not meant for public consumption.

        """
        self.widget.SetConverter(converter)

    def set_spin_wrap(self, wrap):
        """ Updates the wrap value of the spin box.

        """
        self.widget.SetWrap(wrap)

