from traits.api import Str

from .i_element import IElement


class IHtml(IElement):
    """ A simple widget for displaying HTML.
    
    Attributes
    ----------
    text : Str
        The HTML to be rendered.
    
    """
    text = Str


