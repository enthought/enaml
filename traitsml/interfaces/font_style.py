from traits.api import HasTraits, Float, Bool, Tuple, List, Enum, Str

from ..constants import Color


class FontStyle(HasTraits):
    """Styles for text, similar to Cascading Style Sheets."""
    
    # A List of font families: the first available one will be used.
    families = List(Str)
    
    # The size of a font, in pixels (px).
    size = Float
    
    # The foreground color of a font.
    fg_color = Tuple(Color.DEFAULT)
    
    # The background color of a font.
    bg_color = Tuple(Color.DEFAULT)
    
    # Specify if a font is bold.
    bold = Bool(False)
    
    # Determine whether a font is italicized.
    italic = Bool(False)
    
    # A line below, through, or above text.
    text_decoration = Enum('underline', 'strike', 'overline')
    
    
