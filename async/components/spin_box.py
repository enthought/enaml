#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Int, Bool, Range, Instance, on_trait_change

from .control import Control

from ..validation import AbstractValidator, IntValidator

class SpinBox(Control):
    """ A spin box widget which manipulates integer values.

    """
    #: The minimum value for the spin box. Defaults to 0.
    minimum = Int(0)

    #: The maximum value for the spin box. Defaults to 100.
    maximum = Int(100)

    #: The step size for the spin box. Defaults to 1.
    single_step = Int(1)

    #: The current integer value for the spin box, constrained to
    #: low <= value <= high.
    value = Range('low', 'high')

    #: A validator object to convert to and from a spin box integer
    #: and a unicode string for display. The format method will be 
    #: called with an integer and should return a string for display. 
    #: The convert method will be passed a string and should return 
    #: an int or raise a ValueError if the string cannot be converted. 
    #: If the conversion is succesful but the returned int does not fall
    #: within the allowed range of the spin box, then the spin box will
    #: not be updated. The default validator is a simple IntValidator.
    validator = Instance(AbstractValidator, factory=IntValidator)

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

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    @on_trait_change('maximum, minimum, single_step, tracking, validator, \
                     value, wrap')
    def sync_object_state(self, name, new):
        """ Notify the client component of updates to the object state.

        """
        msg = 'set_' + name
        self.send(msg, {'value':new})

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(SpinBox, self).initial_attrs()
        attrs = {
            'maximum' : self.maximum,
            'minimum' : self.minimum,
            'single_step' : self.single_step,
            'tracking' : self.tracking,
            'validator' : self.validator,
            'value' : self.value,
            'wrap' : self.wrap
        }
        super_attrs.update(attrs)
        return super_attrs
