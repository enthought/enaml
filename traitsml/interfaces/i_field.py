from traits.api import Any, Bool, Callable 

from .i_line_edit import ILineEdit


class IField(ILineEdit):
    """ A basic value field that performs validation/conversion
    on the text value. It is a subclass of LineEdit.

    Attributes
    ----------
    error : boolean. Whether or not the from_string or to_string
            callables raised an exception during conversion.
    
    from_string : The callable to be called to convert the string 
                  in the the text box to the proper python value.

    to_string : The callable to be called to convert the python
                value to a string for display.

    value : The python value for display in the field.

    """
    error = Bool

    from_string = Callable(str)
    
    to_string = Callable(str)
      
    value = Any
 
    
