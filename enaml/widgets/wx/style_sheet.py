from ...enums import SizePolicy
from ...util.style_sheet import StyleSheet


WX_STYLE_SHEET = StyleSheet({
    "*": {
        "size_hint": (-1, -1),
        "size_policy": SizePolicy.EXPANDING,
        "stretch": 0,
        "spacing": 2,
    },
    "PushButton": {
        "size_policy": SizePolicy.MINIMUM,
    },
    "CheckBox": {
        "size_policy": SizePolicy.MINIMUM,
    },
    "SpinBox": {
        "size_policy": SizePolicy.MINIMUM,
        "stretch": 1,
    },
    "ComboBox": {
        "size_policy": SizePolicy.MINIMUM,
        "stretch": 1,
    },
    "Html": {
        "stretch": 2,
    },
    "Slider": {
        "stretch": 1,
    },
    "Panel": {
        "stretch": 1,
    },
    "LineEdit": {
        "stretch": 1,
    },
    "Field": {
        "stretch": 1,
    },
    "Label": {
        "stretch": 1,
    },
    "Spacer": {
        "stretch": 2,
    },

    #---------------------------------------------------------------------------
    # Convienence style classes
    #---------------------------------------------------------------------------

    # size_policy
    ".fixed": {
        "size_policy": SizePolicy.MINIMUM,
    },
    ".expanding": {
        "size_policy": SizePolicy.EXPANDING,
    },

    # stretch
    ".no_stretch": {
        "stretch": 0
    },
    ".stretch": {
        "stretch": 1,
    },
    ".x_stretch": {
        "stretch": 2,
    },
    ".xx_stretch": {
        "stretch": 3,
    },
    ".X_stretch": {
        "stretch": 4,
    },
    ".XX_stretch": {
        "stretch": 5,
    },

    # spacing
    ".no_space": {
        "spacing": 0,
    },
    ".space": {
        "spacing": 2,
    },
    ".x_space": {
        "spacing": 5,
    },
    ".xx_space": {
        "spacing": 10,
    },
    ".X_space": {
        "spacing": 20,
    },
    ".XX_space": {
        "spacing": 40,
    },
})

