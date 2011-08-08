from traits.api import Any, Bool, Callable 

from ..registry import register_element
from .i_line_edit import ILineEdit


@register_element
class IField(ILineEdit):
    """ A basic value field that performs validation/conversion
    on the text value. It is a subclass of LineEdit.

    """
    # Whether or not the from_string callable raised an 
    # exception during conversion.
    error = Bool

    # The callable to be called to convert the string in the 
    # the text box to the proper python value. Defaults to str.
    from_string = Callable(str)
    
    # The callable to be called to convert the python value
    # to a string for display. Defaults to str.
    to_string = Callable(str)
      
    # The python value for display in the field.
    value = Any
 
    
