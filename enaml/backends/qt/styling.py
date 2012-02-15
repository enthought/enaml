#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui


def q_color_from_color(color):
    """ Converts an enaml Color into a QtGui.QColor instance.

    """
    if not color:
        res = QtGui.QColor()
    else:
        res = QtGui.QColor(*color)
    return res


font_style_map = {
    'normal': QtGui.QFont.StyleNormal,
    'italic': QtGui.QFont.StyleItalic,
    'oblique': QtGui.QFont.StyleOblique,
}


font_family_hint_map = {
    'any': QtGui.QFont.AnyStyle,
    'sans_serif': QtGui.QFont.SansSerif,
    'helvetica': QtGui.QFont.Helvetica,
    'serif': QtGui.QFont.Serif,
    'times': QtGui.QFont.Times,
    'type_writer': QtGui.QFont.TypeWriter,
    'courier': QtGui.QFont.Courier,
    'old_english': QtGui.QFont.OldEnglish,
    'decorative': QtGui.QFont.Decorative,
    'monospace': QtGui.QFont.Monospace,
    'fantasy': QtGui.QFont.Fantasy,
    'cursive': QtGui.QFont.Cursive,
    'system': QtGui.QFont.System,
}


def q_font_from_font(font):
    """ Converts an enaml Font into a QtGui.QFont instance.

    """
    q_font = QtGui.QFont()
    if font.family:
        q_font.setFamily(font.family)
    if font.point_size != -1:
        q_font.setPointSize(font.point_size)
    if font.weight != -1:
        q_font.setWeight(font.weight)
    if font.style:
        q_font.setStyle(font_style_map[font.style])
    if font.underline:
        q_font.setUnderline(font.underline)
    if font.strikethrough:
        q_font.setStrikeOut(font.strikethrough)
    if font.family_hint:
        q_font.setStyleHint(font_family_hint_map[font.family_hint])
    # XXX more to go, this is enough to test
    return q_font

