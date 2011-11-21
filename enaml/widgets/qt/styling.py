#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui

from ...styling.style_sheet import StyleSheet, style
from ...styling.layout import SizePolicyFlag, Alignment


#-------------------------------------------------------------------------------
# Default Qt style sheet definition
#-------------------------------------------------------------------------------
QT_STYLE_SHEET = StyleSheet(
    
    #---------------------------------------------------------------------------
    # Default style
    #---------------------------------------------------------------------------
    #style("*",
    #    size_policy = "expanding",
    #),

    #---------------------------------------------------------------------------
    # default type overrides
    #---------------------------------------------------------------------------
    #style("PushButton", "CheckBox", "SpinBox", "ComboBox",
    #    size_policy = "preferre",
    #),

    #style("SpinBox", "ComboBox", "Slider", "Panel", "LineEdit", "Field", "Label",
    #    stretch = 1,
    #),

    #style("Html", "Spacer",
    #    stretch = 2,
    #),

    #style("Group", "VGroup", "HGroup",
    #    spacing = 2,
    #),

    style("TableView",
        stretch = 1,
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

#------------------------------------------------------------------------------
# qt styling helper and conversion functions
#------------------------------------------------------------------------------


def q_color_from_color(color):
    """ Converts an enaml Color into a QtGui.QColor instance.
    """
    if not color:
        res = QtGui.QColor()
    else:
        res = QtGui.QColor(color.r, color.g, color.b, color.a)
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
    
