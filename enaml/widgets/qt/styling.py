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
_Q_SIZE_POLICIES = {
    SizePolicyFlag().default(): None,
    SizePolicyFlag().fixed(): QtGui.QSizePolicy.Fixed,
    SizePolicyFlag().minimum(): QtGui.QSizePolicy.Minimum,
    SizePolicyFlag().maximum(): QtGui.QSizePolicy.Maximum,
    SizePolicyFlag().preferred(): QtGui.QSizePolicy.Preferred,
    SizePolicyFlag().expanding(): QtGui.QSizePolicy.Expanding,
    SizePolicyFlag().minimum_expanding(): QtGui.QSizePolicy.MinimumExpanding,
    SizePolicyFlag().ignored(): QtGui.QSizePolicy.Ignored,
}


def set_widget_sizepolicy(widget, policy):
    """ Update the size policy of a QWidget.

    Arguments
    ---------
    widget : QtGui.QWidget
        The Qt widget on which we are updating the size policy.

    policy : enaml.styling.layout.SizePolicy
        An enaml size policy value.
    
    """
    horizontal = _Q_SIZE_POLICIES[policy.horizontal]
    vertical = _Q_SIZE_POLICIES[policy.vertical]
    
    if horizontal is None and vertical is None:
        return
    
    current = widget.sizePolicy()

    if horizontal is None:
        horizontal = current.horizontalPolicy()
    
    if vertical is None:
        vertical = current.verticalPolicy()

    new = QtGui.QSizePolicy(horizontal, vertical)

    widget.setSizePolicy(new)


def q_alignment_from_alignment(align):
    """ Convert an enaml Alignment value into a Qt alignment value.

    Arguments
    ---------
    align : enaml.styling.layout.Alignment
        An alignment value.
    
    Returns
    -------
    result : int
        A Qt alignment value.

    """
    Qt = QtCore.Qt
    res = 0
    if align & Alignment.LEFT:
        res |= Qt.AlignLeft
    if align & Alignment.RIGHT:
        res |= Qt.AlignRight
    if align & Alignment.JUSTIFY:
        res |= Qt.AlignJustify
    if align & Alignment.BOTTOM:
        res |= Qt.AlignBottom
    if align & Alignment.TOP:
        res |= Qt.AlignTop
    if align & Alignment.HCENTER:
        res |= Qt.AlignHCenter
    if align & Alignment.VCENTER:
        res |= Qt.AlignVCenter
    return res


def q_color_from_color(color):
    """ Converts an enaml Color into a QtGui.QColor instance.

    Arguments
    ---------
    color : enaml.styling.color.Color
        An enaml Color object.

    Returns
    -------
    result : QtGui.QColor
        The coverted Qt color object.

    """
    if not color:
        res = QtGui.QColor()
    else:
        res = QtGui.QColor(color.r, color.g, color.b, color.a)
    return res


def set_qwidget_bgcolor(widget, bgcolor):
    """ Set the background color of a QWidget to the color specified by
    the given enaml color or reset the widgets color to the background
    role if the enaml color is invalid.

    Arguments
    ---------
    widget : QtGui.QWidget
        The widget on which we are changing the background color.
    
    bgcolor : enaml.styling.color.Color
        An enaml Color object.

    """
    role = widget.backgroundRole()
    if not bgcolor:
        palette = QtGui.QApplication.instance().palette(widget)
        qcolor = palette.color(role)
        # On OSX, the default color is rendered *slightly* off
        # so a simple workaround is to tell the widget not to
        # auto fill the background.
        widget.setAutoFillBackground(False)
    else:
        qcolor = q_color_from_color(bgcolor)
        # When not using qt style sheets to set the background
        # color, we need to tell the widget to auto fill the 
        # background or the bgcolor won't render at all.
        widget.setAutoFillBackground(True)
    palette = widget.palette()
    palette.setColor(role, qcolor)
    widget.setPalette(palette)


def set_qwidget_fgcolor(widget, fgcolor):
    """ Set the foreground color of a QWidget to the color specified by
    the given enaml color or reset the widgets color to the foreground
    role if the enaml color is invalid.

    Arguments
    ---------
    widget : QtGui.QWidget
        The widget on which we are changing the foreground color.
    
    fgcolor : enaml.styling.color.Color
        An enaml Color object.

    """
    role = widget.foregroundRole()
    if not fgcolor:
        palette = QtGui.QApplication.instance().palette(widget)
        qcolor = palette.color(role)
    else:
        qcolor = q_color_from_color(fgcolor)
    palette = widget.palette()
    palette.setColor(role, qcolor)
    widget.setPalette(palette)

