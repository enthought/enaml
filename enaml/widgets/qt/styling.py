from .qt_api import QtCore, QtGui

from ...color import Color
from ...style_sheet import StyleSheet, style
from ...style_converters import PaddingStyle

#-------------------------------------------------------------------------------
# Default wx style sheet definition
#-------------------------------------------------------------------------------
QT_STYLE_SHEET = StyleSheet(
    
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

    style("SpinBox", "ComboBox", "Slider", "Panel", "LineEdit", "Field", "Label",
        stretch = 1,
    ),

    style("Html", "Spacer",
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
# qt styling helper and conversion functions
#-------------------------------------------------------------------------------
ALIGN_MAP = {
    'top': QtCore.Qt.AlignTop,
    'right': QtCore.Qt.AlignRight,
    'bottom': QtCore.Qt.AlignBottom,
    'left': QtCore.Qt.AlignLeft,
    'hcenter': QtCore.Qt.AlignHCenter,
    'vcenter': QtCore.Qt.AlignVCenter,
    'center': QtCore.Qt.AlignCenter,
}

'''
def wx_color_from_color(color, wx_no_color=wx.NullColor):
    """ Converts an enaml.color.Color into a wx color.

    """
    if color == Color.no_color:
        res = wx_no_color
    else:
        res = wx.Color(color.r, color.g, color.b, color.a)
    return res


def compute_sizer_flags(style):
    """ Computes wx sizer flags given a style node.

    """
    get_property = style.get_property
    padding_style = PaddingStyle.from_style_node(style)
    order = [wx.TOP, wx.RIGHT, wx.BOTTOM, wx.LEFT]
    border_flags = 0
    border_amt = -1

    for amt, flag in zip(padding_style.padding, order):
        if amt >= 0:
            border_amt = max(border_amt, amt)
            border_flags |= flag

    sizer_flags = wx.SizerFlags()
    
    if border_amt >= 0:
        sizer_flags.Border(border_flags, amt)

    align = get_property("align")
    if isinstance(align, basestring):
        align_spec = align.split()
        align_flags = 0
        for align in align_spec:
            align_flags |= ALIGN_MAP.get(align, 0)
        if align_flags != 0:
            sizer_flags.Align(align_flags)
    
    size_policy = get_property("size_policy")
    if isinstance(size_policy, basestring):
        size_policy_spec = size_policy.strip()
        if size_policy_spec == 'expanding':
            sizer_flags.Expand()

    stretch = get_property("stretch")
    if isinstance(stretch, int) and stretch >= 0:
        sizer_flags.Proportion(stretch)

    return sizer_flags

'''