#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Int, Bool, Range

from .constraints_widget import ConstraintsWidget


class SpinBox(ConstraintsWidget):
    """ A spin box widget which manipulates integer values.

    """
    #: The minimum value for the spin box. Defaults to 0.
    minimum = Int(0)

    #: The maximum value for the spin box. Defaults to 100.
    maximum = Int(100)

    #: The step size for the spin box. Defaults to 1.
    single_step = Int(1)

    #: The current integer value for the spin box, constrained to
    #: minimum <= value <= maximum.
    value = Range('minimum', 'maximum')

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
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return the dict of creation attributes for the control.

        """
        super_attrs = super(SpinBox, self).creation_attributes()
        attrs = {
            'maximum' : self.maximum,
            'minimum' : self.minimum,
            'single_step' : self.single_step,
            'tracking' : self.tracking,
            'value' : self.value,
            'wrap' : self.wrap
        }
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(SpinBox, self).bind()
        attrs = (
            'maximum', 'minimum', 'single_step', 'tracking', 'validator',
            'value', 'wrap'
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_changed(self, payload):
        """ Handle the 'event-changed' action from the client widget.

        """
        self.set_guarded(value=payload['value'])

