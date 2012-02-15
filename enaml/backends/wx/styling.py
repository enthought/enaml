#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx


def wx_color_from_color(color):
    """ Converts an Enaml Color into a wxColor.

    """
    if not color:
        res = wx.NullColor
    else:
        res = wx.Color(*color)
    return res


font_style_map = {
    'normal': wx.FONTSTYLE_NORMAL,
    'italic': wx.FONTSTYLE_ITALIC,
    'oblique': wx.FONTSTYLE_SLANT,
}


font_family_hint_map = {
    'any': wx.FONTFAMILY_DEFAULT,
    'sans_serif': wx.FONTFAMILY_SWISS,
    'helvetica': wx.FONTFAMILY_DEFAULT,
    'times': wx.FONTFAMILY_ROMAN,
    'type_writer': wx.FONTFAMILY_TELETYPE,
    'courier': wx.FONTFAMILY_MODERN,
    'old_english': wx.FONTFAMILY_DEFAULT,
    'decorative': wx.FONTFAMILY_DECORATIVE,
    'monospace': wx.FONTFAMILY_MODERN,
    'fantasy': wx.FONTFAMILY_DEFAULT,
    'cursive': wx.FONTFAMILY_SCRIPT,
    'system': wx.FONTFAMILY_DEFAULT
}


# A cache of the default font which is created on demand
_cached_wx_default_font = None
def _wx_default_font():
    global _cached_wx_default_font
    if _cached_wx_default_font is None:
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        _cached_wx_default_font = font
    return _cached_wx_default_font


def wx_font_from_font(font):
    """ Converts an Enaml Font into a wxFont.

    """
    point_size = font.point_size
    if point_size != -1:
        wx_point_size = point_size
    else:
        wx_point_size = _wx_default_font().GetPointSize()

    wx_family = font_family_hint_map[font.family_hint]
    
    wx_style = font_style_map[font.style]

    weight = font.weight
    if weight < 45:
        wx_weight = wx.FONTWEIGHT_LIGHT
    elif weight > 55:
        wx_weight = wx.FONTWEIGHT_BOLD
    else:
        wx_weight = wx.FONTWEIGHT_NORMAL

    wx_underline = font.underline

    wx_face = font.family
    if not wx_face:
        wx_face = _wx_default_font().GetFaceName()

    wx_font = wx.Font(
        wx_point_size,
        wx_family,
        wx_style,
        wx_weight,
        wx_underline,
        wx_face
    )

    return wx_font

