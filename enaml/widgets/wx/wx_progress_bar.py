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
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.Gauge.

        """
        self.widget = wx.Gauge(self.parent_widget())

    def initialize(self):
        super(WXControl, self).initialize()
        shell = self.shell_obj
        self.shell_minimum_changed(shell.minimum)
        self.shell_maximum_changed(shell.maximum)
        self.shell_value_changed(shell.value)

    #--------------------------------------------------------------------------
    # Abstract implementation methods
    #--------------------------------------------------------------------------
    def shell_value_changed(self, value):
        gauge_value = value - self.shell_obj.minimum
        self.widget.SetValue(gauge_value)

    def shell_minimum_changed(self, minimum):
        gauge_range = self.shell_obj.maximum - minimum
        self.widget.SetRange(gauge_range)

    def shell_maximum_changed(self, maximum):
        gauge_range = maximum - self.shell_obj.minimum
        self.widget.SetRange(gauge_range)


