from traits.api import Str

from .i_element import IElement


class IHtml(IElement):
    """ A simple widget for displaying HTML.
    
    Attributes
    ----------
    text : string. The html to be rendered.
    
    """
    text = Str


