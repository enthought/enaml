from traits.api import Int, Str, Callable, Bool, Range, Instance

from .control import IControlImpl, Control


class ISpinBoxImpl(IControlImpl):

    def parent_low_changed(self, low):
        raise NotImplementedError
    
    def parent_high_changed(self, high):
        raise NotImplementedError
    
    def parent_step_changed(self, step):
        raise NotImplementedError
    
    def parent_value_changed(self, value):
        raise NotImplementedError
    
    def parent_prefix_changed(self, prefix):
        raise NotImplementedError
    
    def parent_suffix_changed(self, suffix):
        raise NotImplementedError
    
    def parent_special_value_text_changed(self, special_value_text):
        raise NotImplementedError
    
    def parent_to_string_changed(self, to_string):
        raise NotImplementedError
    
    def parent_from_string_changed(self, from_string):
        raise NotImplementedError
    
    def parent_wrap_changed(self, wrap):
        raise NotImplementedError
    

class SpinBox(Control):
    """ A spin box widget.
   
    Attributes
    ----------
    low : Int
        The minimum value for the spin box.

    high : Int
        The maximum value for the spin box.
    
    step : Int
        The amount to increase or decrease the value per click.

    value : Range('low', 'high')
        The current value for the spin box, constrained to low-high.

    prefix : Str
        The prefix string to display in the spin box.

    suffix : Str
        The suffix string to display in the spin box.
    
    special_value_text : Str
        An optional string to display when the user selects the 
        minimum value in the spin box.

    to_string : Callable
        An optional callable that takes one argument to convert the 
        integer value to text to display in the spin box.

    from_string : Callable
        An optional callable that takes one argument to convert the 
        user typed string to an integer value.

    wrap : Bool
        If True, the spin box will wrap around at its extremes.

    """
    low = Int

    high = Int

    step = Int

    value = Range('low', 'high')

    prefix = Str

    suffix = Str

    special_value_text = Str

    to_string = Callable(lambda val: str(val))

    from_string = Callable(lambda val: int(val))

    wrap = Bool

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ISpinBoxImpl)

