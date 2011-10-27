#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from ...styling.style_sheet import StyleSheet, style

#-------------------------------------------------------------------------------
# Default wx style sheet definition
#-------------------------------------------------------------------------------
WX_STYLE_SHEET = StyleSheet(
    
    #---------------------------------------------------------------------------
    # Default style
    #---------------------------------------------------------------------------
    style("*",
        size_policy = "expanding",
    ),

    #---------------------------------------------------------------------------
    # default type overrides
    #---------------------------------------------------------------------------
    style("PushButton", "CheckBox", "SpinBox", "ComboBox",
        size_policy = "minimum",
    ),

    style("SpinBox", "ComboBox", "Slider", "Panel", "LineEdit", "Field", 
        "Label", "TableView",
        stretch = 1,
    ),

    style("Html", "Spacer", "EnableCanvas",
        stretch = 2,
    ),

    style("Group", "VGroup", "HGroup",
        spacing = 2,
    ),

    #---------------------------------------------------------------------------
    # Convienence style classes
    #---------------------------------------------------------------------------
    style(".error_colors",
        background_color = "error",
        color = "nocolor",
    ),

    style(".normal_colors",
        background_color = "nocolor",
        color = "nocolor",
    ),

    style(".fixed",
        size_policy = "minimum",
        stretch = 0,
    ),

    style(".expanding",
        size_policy = "expanding",
    ),

    style(".no_stretch",
        stretch = 0,
    ),

    style(".stretch",
        stretch = 1,
    ),

    style(".x_stretch",
        stretch = 2,
    ),

    style(".xx_stretch",
        stretch = 3,
    ),

    style(".X_stretch",
        stretch = 4,
    ),

    style(".XX_stretch",
        stretch = 5,
    ),

    style(".no_padding",
        padding = 0,
    ),

    style(".padding",
        padding = 2,
    ),

    style(".x_padding",
        padding = 5,
    ),

    style(".xx_padding",
        padding = 10,
    ),

    style(".X_padding",
        padding = 20,
    ),

    style(".XX_padding",
        padding = 40,
    ),

)

#-------------------------------------------------------------------------------
# wx styling helper and conversion functions
#-------------------------------------------------------------------------------
ALIGN_MAP = {
    'top': wx.ALIGN_LEFT,
    'right': wx.ALIGN_RIGHT,
    'bottom': wx.ALIGN_BOTTOM,
    'left': wx.ALIGN_LEFT,
    'hcenter': wx.ALIGN_CENTER_HORIZONTAL,
    'vcenter': wx.ALIGN_CENTER_VERTICAL,
    'center': wx.ALIGN_CENTER,
}


def wx_color_from_color(color, wx_no_color=wx.NullColor):
    """ Converts an enaml.color.Color into a wx color.

    """
    if not color:
        res = wx.NullColor
    else:
        res = wx.Color(color.r, color.g, color.b, color.a)
    return res


def set_wxwidget_bgcolor(widget, bgcolor):
    """ Set the background color of a wxWidget to the color specified by
    the given enaml color or reset the widgets color to the background
    role if the enaml color is invalid.

    Arguments
    ---------
    widget : wx.Window
        The widget on which we are changing the background color.
    
    bgcolor : enaml.styling.color.Color
        An enaml Color object.

    """
    wx_color = wx_color_from_color(bgcolor)
    widget.SetBackgroundColour(wx_color)
    widget.Refresh()


def set_wxwidget_fgcolor(widget, fgcolor):
    """ Set the foreground color of a wxWidget to the color specified by
    the given enaml color or reset the widgets color to the foreground
    role if the enaml color is invalid.

    Arguments
    ---------
    widget : wx.Window
        The widget on which we are changing the foreground color.
    
    fgcolor : enaml.styling.color.Color
        An enaml Color object.

    """
    wx_color = wx_color_from_color(fgcolor)
    widget.SetForegroundColour(wx_color)
    widget.Refresh()


def compute_sizer_flags(style):
    """ Computes wx sizer flags given a style node.

    """
    return wx.SizerFlags().Expand().Proportion(1)

    # get_property = style.get_property
    # order = [wx.TOP, wx.RIGHT, wx.BOTTOM, wx.LEFT]
    # border_flags = 0
    # border_amt = -1

    # for amt, flag in zip(padding_style.padding, order):
    #     if amt >= 0:
    #         border_amt = max(border_amt, amt)
    #         border_flags |= flag

    # sizer_flags = wx.SizerFlags()
    
    # if border_amt >= 0:
    #     sizer_flags.Border(border_flags, amt)

    # align = get_property("align")
    # if isinstance(align, basestring):
    #     align_spec = align.split()
    #     align_flags = 0
    #     for align in align_spec:
    #         align_flags |= ALIGN_MAP.get(align, 0)
    #     if align_flags != 0:
    #         sizer_flags.Align(align_flags)
    
    # size_policy = get_property("size_policy")
    # if isinstance(size_policy, basestring):
    #     size_policy_spec = size_policy.strip()
    #     if size_policy_spec == 'expanding':
    #         sizer_flags.Expand()

    # stretch = get_property("stretch")
    # if isinstance(stretch, int) and stretch >= 0:
    #     sizer_flags.Proportion(stretch)

    # return sizer_flags

