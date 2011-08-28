from traits.api import Str

from .i_element import IElement


class IHtml(IElement):
    """ A simple widget for displaying HTML.
    
    Attributes
    ----------
    source : Str
        The Html source code to be rendered.
    
    """
    source = Str

