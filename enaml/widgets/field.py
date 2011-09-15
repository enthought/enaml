from traits.api import Any, Bool, Callable, Instance, Property

from .line_edit import ILineEditImpl, LineEdit


class IFieldImpl(ILineEditImpl):

    def parent_from_string_changed(self, from_string):
        raise NotImplementedError
    
    def parent_to_string_changed(self, to_string):
        raise NotImplementedError
    
    def parent_value_changed(self, value):
        raise NotImplementedError


class Field(LineEdit):
    """ A basic value field which subclasses from LineEdit.

    A Field performs validation/conversion on the text value and
    updates the 'error' attribute when conversion fails.

    Attributes
    ----------
    from_string : Callable
        A callable to convert the string in the the text box to a
        Python value.

    to_string : Callable
        A callable to convert the Python value to a string for display.

    value : Any
        The Python value to display in the field.

    """
    from_string = Callable
    
    to_string = Callable
      
    value = Any
    
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IFieldImpl)

