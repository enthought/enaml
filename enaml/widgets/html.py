from traits.api import Str

from .control import Control


class Html(Control):
    """ A simple widget for displaying HTML.
    
    Attributes
    ----------
    source : Str
        The Html source code to be rendered.
    
    """
    source = Str

