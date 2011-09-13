from ...util.style_sheet import StyleSheet, style


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

