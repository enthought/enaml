import wx

from ...color import Color
from ...util.style_sheet import StyleSheet, style, NO_STYLE


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

    style("SpinBox", "ComboBox", "Slider", "Panel", "LineEdit", "Field", "Label",
        stretch = 1,
    ),

    style("Html", "Spacer",
        stretch = 2,
    ),

    style("Group", "VGroup", "HGroup",
        border = 5,
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

    style(".no_border",
        border_width = 0,
    ),

    style(".border",
        border_width = 2,
    ),

    style(".x_border",
        border_width = 5,
    ),

    style(".xx_border",
        border_width = 10,
    ),

    style(".X_border",
        border_width = 20,
    ),

    style(".XX_border",
        border_width = 40,
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


def wx_color_from_color(value, wx_no_color=wx.NullColor):
    """ Converts an enaml.color.Color into a wx color.

    """
    if value is NO_STYLE:
        color = Color.no_color
    elif isinstance(value, basestring):
        color = Color.from_string(value.strip())
    elif isinstance(value, Color):
        color = value
    else:
        color = Color.no_color

    if color == Color.no_color:
        res = wx_no_color
    else:
        res = wx.Color(color.r, color.g, color.b, color.a)

    return res


def compute_sizer_flags(style):

    get_tag = style.get_tag

    border_top = None
    border_right = None
    border_bottom = None
    border_left = None

    # XXX we need a better way to parse the border shorthand
    border_width = get_tag("border_width")
    if border_width is not NO_STYLE:
        try:
            border_iter = iter(border_width)
        except TypeError:
            border_iter = iter((border_width,))
    else:
        border = get_tag("border")
        if border is not NO_STYLE:
            try:
                border_iter = iter(border)
            except TypeError:
                border_iter = iter((border,))
        else:
            border_iter = ()
    
    border_widths = [width for width in border_iter if isinstance(width, int)]
    n = len(border_widths)
    sides = 0
    if n == 0:
        pass
    elif n == 1:
        width = border_widths[0]
        if width >= 0:
            border_top = border_right = border_bottom = border_left = width
            sides |= wx.ALL
    elif n == 2: 
        width1, width2 = border_widths
        if width1 >= 0:
            border_bottom = border_top = width1
            sides |= (wx.TOP | wx.BOTTOM)
        if width2 >= 0:
            border_left = border_right = width2
            sides |= (wx.RIGHT | wx.LEFT)
    elif n == 3:
        width1, width2, width3 = border_widths
        if width1 >= 0:
            border_top = width1
            sides |= wx.TOP
        if width2 >= 0:
            border_right = border_left = width2
            sides |= (wx.RIGHT | wx.LEFT)
        if width3 >= 0:
            border_bottom = width3
            sides |= wx.BOTTOM
    else:
        width1, width2, width3, width4 = border_widths
        if width1 >= 0:
            border_top = width1
            sides |= wx.TOP
        if width2 >= 0:
            border_right = width2
            sides |= wx.RIGHT
        if width3 >= 0:
            border_bottom = width3
            sides |= wx.BOTTOM
        if width4 >= 0:
            border_left = width4
            sides |= wx.LEFT

    st = get_tag("border_top_width")
    if st is not NO_STYLE:
        border_top = st
        sides |= wx.TOP
    
    sr = get_tag("border_right_width")
    if sr is not NO_STYLE:
        border_right = sr
        sides |= wx.RIGHT

    sb = get_tag("border_bottom_width")
    if sb is not NO_STYLE:
        border_bottom = sb
        sides |= wx.BOTTOM

    sl = get_tag("border_left_width")
    if sl is not NO_STYLE:
        border_left = sl
        sides |= wx.LEFT

    amt = max(border_top, border_right, border_bottom, border_left, -1)
    
    spacing = get_tag("spacing")
    if spacing is not NO_STYLE and spacing > 0:
        if isinstance(spacing, int):
            amt += spacing

    flags = wx.SizerFlags()
    
    if amt >= 0:
        flags.Border(sides, amt)

    align = get_tag("align")
    if align is not NO_STYLE:
        try:
            align_spec = align.split()
        except AttributeError:
            pass
        else:
            align_flags = 0
            for align in align_spec:
                align_flags |= ALIGN_MAP.get(align, 0)
            flags.Align(align_flags)
    
    size_policy = get_tag("size_policy")
    if size_policy is not NO_STYLE:
        try:
            size_policy_spec = style.size_policy.strip()
        except AttributeError:
            pass
        else:
            if size_policy_spec == 'expanding':
                flags.Expand()
    
    stretch = get_tag("stretch")
    if stretch is not NO_STYLE and stretch >= 0:
        try:
            flags.Proportion(stretch)
        except TypeError:
            pass

    return flags

