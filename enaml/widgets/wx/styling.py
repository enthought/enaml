#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx


def wx_color_from_color(color):
    """ Converts an enaml.color.Color into a wx color.

    """
    if not color:
        res = wx.NullColor
    else:
        res = wx.Color(*color)
    return res

