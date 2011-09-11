import wx

from ...util.style_sheet import NO_STYLE


ALIGN_MAP = {
    'top': wx.ALIGN_LEFT,
    'right': wx.ALIGN_RIGHT,
    'bottom': wx.ALIGN_BOTTOM,
    'left': wx.ALIGN_LEFT,
    'hcenter': wx.ALIGN_CENTER_HORIZONTAL,
    'vcenter': wx.ALIGN_CENTER_VERTICAL,
    'center': wx.ALIGN_CENTER,
}


def rgba_to_wx_color(r, g, b, a=1.0):
    """ Converts 0.0 - 1.0 floating point rgb(a) values into a 
    wx.Colour object.

    """
    r = max(0, min(255, int(255 * r)))
    g = max(0, min(255, int(255 * g)))
    b = max(0, min(255, int(255 * b)))
    a = max(0, min(255, int(255 * a)))
    return wx.Color(r, g, b, a)


def compute_sizer_flags(style):

    border_top = None
    border_right = None
    border_bottom = None
    border_left = None

    # XXX we need a better way to parse the border shorthand
    border_width = style.border_width
    if border_width is not NO_STYLE:
        try:
            border_iter = iter(border_width)
        except TypeError:
            border_iter = iter((border_width,))
    else:
        border = style.border
        if border is not NO_STYLE:
            try:
                border_iter = iter(border)
            except TypeError:
                border_iter = iter((border,))
        else:
            border_iter = ()
    
    border_widths = [width for width in border_iter if isinstance(width, int)]
    n = len(border_widths)
    if n == 0:
        sides = 0
    elif n == 1:
        width = border_widths[0]
        border_top = border_right = border_bottom = border_left = width
        sides = wx.ALL
    elif n == 2:
        border_top, border_right = border_widths
        border_bottom = border_top
        border_left = border_right
        sides = wx.ALL
    elif n == 3:
        border_top, border_right, border_bottom = border_widths
        border_left = border_right
        sides = wx.ALL
    else:
        border_widths = border_widths[:4]
        border_top, border_right, border_bottom, border_left = border_widths
        sides = wx.ALL

    st = style.border_top_width
    if st is not NO_STYLE:
        border_top = st
        sides |= wx.TOP
    
    sr = style.border_right_width
    if sr is not NO_STYLE:
        border_right = sr
        sides |= wx.RIGHT

    sb = style.border_bottom_width
    if sb is not NO_STYLE:
        border_bottom = sb
        sides |= wx.BOTTOM

    sl = style.border_left_width
    if sl is not NO_STYLE:
        border_left = sl
        sides |= wx.LEFT

    amt = max(border_top, border_right, border_bottom, border_left, -1)
    spacing = style.spacing
    if spacing is not NO_STYLE:
        if isinstance(spacing, int):
            amt += spacing

    flags = wx.SizerFlags()
    flags.Border(sides, amt)

    align = style.align
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
    
    size_policy = style.size_policy
    if size_policy is not NO_STYLE:
        try:
            size_policy_spec = style.size_policy.strip()
        except AttributeError:
            pass
        else:
            if size_policy_spec == 'expanding':
                flags.Expand()
    
    stretch = style.stretch
    if stretch is not NO_STYLE:
        try:
            flags.Proportion(stretch)
        except TypeError:
            pass

    return flags

