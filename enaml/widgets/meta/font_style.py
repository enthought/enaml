#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Interface, Float, Bool, Tuple, List, Enum, Str

from ..constants import Color


class IFontStyle(Interface):
    """Styles for text, similar to Cascading Style Sheets.

    Attributes
    ----------
    family : List
        A prioritized List of font families.
        E.g., "times" or "serif".

    face : List
        A prioritized list of fonts within a family.
        For example, "Times Roman".

    size : Float
        The size of a font, in pixels (px).

    fg_color : Tuple
        The foreground color of a font.

    bg_color : Tuple
        The background color of a font.

    bold : Bool
        Whether text is bold.

    italic : Bool
        Whether text is italicized or not.

    text_decoration : Enum
        A line below, through, or above text. 

    """
    family = List(Str)

    face = List(Str)    

    size = Float
    
    fg_color = Tuple(Color.DEFAULT)
    
    bg_color = Tuple(Color.DEFAULT)
    
    bold = Bool(False)
    
    italic = Bool(False)
    
    text_decoration = Enum('underline', 'strike', 'overline')
    
    
