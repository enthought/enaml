from traits.api import Any, Bool, Callable, Instance, Property

from .line_edit import ILineEditImpl, LineEdit

from ..util.decorators import protected


class IFieldImpl(ILineEditImpl):

    def parent_from_string_changed(self, from_string):
        raise NotImplementedError
    
    def parent_to_string_changed(self, to_string):
        raise NotImplementedError
    
    def parent_value_changed(self, value):
        raise NotImplementedError


@protected('_error', '_exception')
class Field(LineEdit):
    """ A basic value field which subclasses from LineEdit.

    A Field performs validation/conversion on the text value and
    updates the 'error' attribute when conversion fails.

    Attributes
    ----------
    error : Property(Bool)
        A read only property which indicates whether or not the 
        `from_string` or `to_string` callables raised an exception 
        during conversion.
    
    exception : Property(Instance(Exception))
        A read only property which holds the exception raised (if any) 
        during coversion.
    
    from_string : Callable
        A callable to convert the string in the the text box to a
        Python value.

    to_string : Callable
        A callable to convert the Python value to a string for display.

    value : Any
        The Python value to display in the field.
    
    _error : Bool
        A protected attribute that is used by the implementation object
        to set the value of error.
    
    _exception: Instance(Exception)
        A protected attribute that is used by the implementation object
        to set the value of exception.

    """
    error = Property(Bool, depends_on='_error')

    exception = Property(Instance(Exception), depends_on='_exception')

    from_string = Callable
    
    to_string = Callable
      
    value = Any
    
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IFieldImpl)

    def _get_error(self):
        return self._error
    
    def _get_exception(self):
        return self._exception

