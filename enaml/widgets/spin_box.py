#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Int, Str, Callable, Bool, Range, Instance

from .control import Control, AbstractTkControl

from ..converters import Converter, IntConverter


class AbstractTkSpinBox(AbstractTkControl):

    @abstractmethod
    def shell_low_changed(self, low):
        raise NotImplementedError

    @abstractmethod
    def shell_high_changed(self, high):
        raise NotImplementedError

    @abstractmethod
    def shell_step_changed(self, step):
        raise NotImplementedError

    @abstractmethod
    def shell_value_changed(self, value):
        raise NotImplementedError

    @abstractmethod
    def shell_prefix_changed(self, prefix):
        raise NotImplementedError

    @abstractmethod
    def shell_suffix_changed(self, suffix):
        raise NotImplementedError

    @abstractmethod
    def shell_special_value_text_changed(self, special_value_text):
        raise NotImplementedError

    @abstractmethod
    def shell_converter_changed(self, converter):
        raise NotImplementedError

    @abstractmethod
    def shell_wrap_changed(self, wrap):
        raise NotImplementedError
    

class SpinBox(Control):
    """ A spin box widget.

    """
    #: The minimum value for the spin box. Defautls to 0.
    low = Int

    #: The maximum value for the spin box. Defaults to 100.
    high = Int(100)

    # The maximum value for the spin box. Defaults to 1.
    step = Int(1)

    #: The current value for the spin box, constrained to low-high.
    value = Range('low', 'high')

    #: The prefix string to display in the spin box.
    prefix = Str

    #: The suffix string to display in the spin box.
    suffix = Str

    #: An optional string to display when the user selects the 
    #: minimum value in the spin box.
    special_value_text = Str

    # XXX - what is this actually doing?
    #: A converter object to convert to and from the widget value
    converter = Instance(Converter, factory=IntConverter, args=())

    # XXX - what is this?? 
    #: An optional callable that takes a one argument and checks
    #: if it is a valid text value.  Must return an enums.Validity
    #: value.  It a from_string is supplied without a validate_string,
    #: the SpinBox will consider the input acceptable if from_string
    #: does not raise an exception, and intermediate otherwise.
    validate_string = Callable

    #: If True, the spin box will wrap around at its extremes.
    wrap = Bool

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkSpinBox)

