from traits.api import Any, Bool, Callable 

from .i_line_edit import ILineEdit


class IField(ILineEdit):
    """ A basic value field that performs validation/conversion
    on the text value. It is a subclass of LineEdit.

    Attributes
    ----------
    error : Bool
        Whether or not the `from_string` or `to_string`
        callables raised an exception during conversion.
    
    from_string : Callable
        A callable to convert the string 
        in the the text box to the proper Python value.

    to_string : Callable
        A callable to convert the Python
        value to a string for display.

    value : Any
        The Python value to display in the field.

    """
    error = Bool

    from_string = Callable(str)
    
    to_string = Callable(str)
      
    value = Any
 
    
