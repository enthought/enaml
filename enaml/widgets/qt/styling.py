from .qt_api import QtCore, QtGui

from traits.api import HasTraits, Instance, Dict

from ...color import Color
from ...style_sheet import StyleSheet, StyleHandler, style
from ...style_converters import PaddingStyle, color_from_color_style

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

class QtStyleHandler(StyleHandler):
    """ StyleHandler subclass that understands how to set styles via Qt style sheets
    
    Attributes
    ----------
    
    widget : QWidget
        The underlying QWidget that we are interacting with.
    
    _qt_stylesheet_values : Dict
        A dictionary holding the current state.
    """

    widget = Instance(QtGui.QWidget)
    
    _qt_stylesheet_values = Dict

    def set_style_value(self, value, tag, converter):
        """Set the style given by the tag to the value in a generic way for Qt.
        
        This uses Qt's style sheet mechanism.
        
        Arguments
        ---------
        
        value : style_value
            The string representation of the style's value.
        
        tag : string
            The style tag that is being set.
        
        args : callable
            Callable that converts Enaml stylesheet value to Qt stylehseet
            values of the appropriate type for the tag.
        """
        qt_value = converter(value)
        key = tag.replace('_', '-')
        if qt_value is not None:
            self._qt_stylesheet_values[key] = qt_value
        else:
            self._qt_stylesheet_values.pop(key, None)
        stylesheet = generate_qt_stylesheet(self.widget.__class__.__name__,
                self._qt_stylesheet_values)         
        self.widget.setStyleSheet(stylesheet)


def generate_qt_stylesheet(class_name, values):
    """ Generate a Qt stylesheet string
    
    Arguments
    ---------
    
    class_name : string
        The name of the Qt class that is having its stylesheet set.
    
    values : dictionary
        A dictionary whose keys are Qt stylesheet property names and
        whose values are the corresponding string values to be used in
        the stylesheet.
    """
    return (class_name + ' { ' +
        '; '.join(key+': '+value for key, value in values.items()) +
    ' }' )


ALIGN_MAP = {
    'top': QtCore.Qt.AlignTop,
    'right': QtCore.Qt.AlignRight,
    'bottom': QtCore.Qt.AlignBottom,
    'left': QtCore.Qt.AlignLeft,
    'hcenter': QtCore.Qt.AlignHCenter,
    'vcenter': QtCore.Qt.AlignVCenter,
    'center': QtCore.Qt.AlignCenter,
}


def qt_color_from_color(color):
    """ Converts an enaml.color.Color into a qt stylesheet color.

    """
    if color == Color.no_color:
        res = None
    else:
        res = 'rgb(%s, %s, %s, %s)' % (color.r, color.g, color.b, color.a)
    return res


def qt_color(color_style):
    color = color_from_color_style(color_style)
    return qt_color_from_color(color)


'''
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