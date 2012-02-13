#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ..progress_bar import AbstractTkProgressBar


class WXProgressBar(WXControl, AbstractTkProgressBar):
    """ WX implementation of ProgressBar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.Gauge.

        """
        self.widget = wx.Gauge(parent)

    def initialize(self):
        """ Initialize the attributes of the progress bar.

        """
        super(WXControl, self).initialize()
        shell = self.shell_obj
        self.set_minimum(shell.minimum)
        self.set_maximum(shell.maximum)
        self.set_value(shell.value)

    #--------------------------------------------------------------------------
    # Abstract Implementation Methods
    #--------------------------------------------------------------------------
    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute of the shell
        object.

        """
        self.set_value(value)

    def shell_minimum_changed(self, minimum):
        """ The change handler for the 'minimum' attribute of the shell
        object.

        """
        self.set_minimum(minimum)
            
    def shell_maximum_changed(self, maximum):
        """ The change handler for the 'maximum' attribute of the shell
        object

        """
        self.set_maximum(maximum)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Sets the value of the progress bar.

        """
        gauge_value = value - self.shell_obj.minimum
        self.widget.SetValue(gauge_value)

    def set_minimum(self, minimum):
        """ Sets the minimum value of the progress bar.

        """
        gauge_range = self.shell_obj.maximum - minimum
        self.widget.SetRange(gauge_range)
    
    def set_maximum(self, maximum):
        """ Sets the maximum value of the progress bar.

        """
        gauge_range = maximum - self.shell_obj.minimum
        self.widget.SetRange(gauge_range)

