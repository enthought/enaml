from traits.api import Str

from .i_element import IElement


class IHtml(IElement):
    """A widget for displaying HTML."""
    
    # A string of text to be rendered as HTML.
    text = Str

