from traits.api import Any, Bool, Callable, Instance

from .i_line_edit import ILineEdit


class IField(ILineEdit):
    """ A basic value field which subclasses from LineEdit.

    A Field performs validation/conversion on the text value and
    updates the 'error' attribute when conversion fails. 

    Attributes
    ----------
    error : Bool
        Whether or not the `from_string` or `to_string` callables 
        raised an exception during conversion.
    
    exception : Instance(Exception)
        The exception raised (if any) during coversion.
    
    from_string : Callable
        A callable to convert the string in the the text box to a
        Python value.

    to_string : Callable
        A callable to convert the Python value to a string for display.

    value : Any
        The Python value to display in the field.

    """
    error = Bool

    exception = Instance(Exception)

    from_string = Callable
    
    to_string = Callable
      
    value = Any
 
