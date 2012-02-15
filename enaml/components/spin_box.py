#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Int, Bool, Range, Instance

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
    def shell_converter_changed(self, converter):
        raise NotImplementedError

    @abstractmethod
    def shell_wrap_changed(self, wrap):
        raise NotImplementedError
    
    @abstractmethod
    def shell_tracking_changed(self, tracking):
        raise NotImplementedError


class SpinBox(Control):
    """ A spin box widget.

    """
    #: The minimum value for the spin box. Defaults to 0.
    low = Int(0)

    #: The maximum value for the spin box. Defaults to 100.
    high = Int(100)

    #: The step size for the spin box. Defaults to 1.
    step = Int(1)

    #: The current integer value for the spin box, constrained to
    #: low <= value <= high.
    value = Range('low', 'high')

    #: A converter object to convert to and from a spin box integer
    #: and a string for display. The to_component method will be called 
    #: with an integer and should return a string for display. The 
    #: from_component method will be passed a string and should return 
    #: an int or raise a ValueError if the string cannot be converted. 
    #: If the conversion is succesful but the returned int does not fall
    #: within the allowed range of the spin box, then the spin box will
    #: not be updated. The default converter is a simple IntConverter
    converter = Instance(Converter, factory=IntConverter)

    #: Whether or not the spin box will wrap around at its extremes. 
    #: Defaults to False.
    wrap = Bool(False)
    
    #: Whether the spin box will update on every key press (True), or
    #: only when enter is pressed or the widget loses focus (False).
    #: Defaults to False.
    tracking = Bool(False)

    #: How strongly a component hugs it's contents' width. SpinBoxes 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkSpinBox)

