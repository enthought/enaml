#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_constraints_widget import WxConstraintsWidget


class WxProgressBar(WxConstraintsWidget):
    """ A Wx implementation of an Enaml ProgressBar.

    """
    #: The minimum value of the progress bar
    _minimum = 0

    #: The maximum value of the progress bar
    _maximum = 100

    def create(self):
        """ Create the underlying progress bar widget.

        """
        self.widget = wx.Gauge(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(WxProgressBar, self).initialize(attrs)
        self.set_minimum(attrs['minimum'])
        self.set_maximum(attrs['maximum'])
        self.set_value(attrs['value'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_minimum(content['minimum'])

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_maximum(content['maximum'])

    def on_action_set_value(self, content):
        """ Handle the 'set_value' action from the Enaml widget.

        """
        self.set_value(content['value'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_minimum(self, value):
        """ Set the minimum value of the progress bar

        """
        self._minimum = value
        self.widget.SetRange(self._maximum - value)

    def set_maximum(self, value):
        """ Set the maximum value of the progress bar

        """
        self._maximum = value
        self.widget.SetRange(value - self._minimum)

    def set_value(self, value):
        """ Set the value of the progress bar

        """
        self.widget.SetValue(value - self._minimum)

