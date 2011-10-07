#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Int, Str, Callable, Bool, Range, Instance, Either

from .control import IControlImpl, Control

from ..converters import Converter, IntConverter


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
    
    def parent_converter_changed(self, converter):
        raise NotImplementedError
    
    def parent_wrap_changed(self, wrap):
        raise NotImplementedError
    

class SpinBox(Control):
    """ A spin box widget.
   
    Attributes
    ----------
    low : Int
        The minimum value for the spin box. Defautls to 0.

    high : Int
        The maximum value for the spin box.  Defaults to 1.
    
    step : Int
        The amount to increase or decrease the value per click.  Defaults to 1.

    value : Range('low', 'high')
        The current value for the spin box, constrained to low-high.

    prefix : Str
        The prefix string to display in the spin box.

    suffix : Str
        The suffix string to display in the spin box.
    
    special_value_text : Str
        An optional string to display when the user selects the 
        minimum value in the spin box.

    converter : Instance(Converter)
        A pair of functions for converting values to, and from, a widget.
        
    validate_string : Callable
        An optional callable that takes a one argument and checks
        if it is a valid text value.  Must return an enums.Validity
        value.  It a from_string is supplied without a validate_string,
        the SpinBox will consider the input acceptable if from_string
        does not raise an exception, and intermediate otherwise.

    wrap : Bool
        If True, the spin box will wrap around at its extremes.

    """
    low = Int

    high = Int(1)

    step = Int(1)

    value = Range('low', 'high')

    prefix = Str

    suffix = Str

    special_value_text = Str

    converter = Instance(Converter, factory=IntConverter, args=())
    
    validate_string = Either(Callable, None)

    wrap = Bool

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ISpinBoxImpl)

