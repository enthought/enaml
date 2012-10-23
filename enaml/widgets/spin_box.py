#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Int, Bool, Range, Unicode

from .control import Control


class SpinBox(Control):
    """ A spin box widget which manipulates integer values.

    """
    #: The minimum value for the spin box. Defaults to 0.
    minimum = Int(0)

    #: The maximum value for the spin box. Defaults to 100.
    maximum = Int(100)

    #: The current integer value for the spin box, constrained to
    #: minimum <= value <= maximum.
    value = Range('minimum', 'maximum')

    #: An optional prefix to include in the displayed text.
    prefix = Unicode

    #: An optional suffix to include in the displayed text.
    suffix = Unicode

    #: Optional text to display when the spin box is at its minimum.
    #: This allows the developer to indicate to the user a special
    #: significance to the minimum value e.g. "Auto"
    special_value_text = Unicode

    #: The step size for the spin box. Defaults to 1.
    single_step = Range(low=1)

    #: Whether or not the spin box is read-only. If True, the user
    #: will not be able to edit the values in the spin box, but they
    #: will still be able to copy the text to the clipboard.
    read_only = Bool(False)

    #: Whether or not the spin box will wrap around at its extremes.
    #: Defaults to False.
    wrapping = Bool(False)

    #: How strongly a component hugs it's contents' width. SpinBoxes
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(SpinBox, self).snapshot()
        attrs = {
            'maximum' : self.maximum,
            'minimum' : self.minimum,
            'value' : self.value,
            'prefix': self.prefix,
            'suffix': self.suffix,
            'special_value_text': self.special_value_text,
            'single_step' : self.single_step,
            'read_only': self.read_only,
            'wrapping' : self.wrapping,
        }
        snap.update(attrs)
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(SpinBox, self).bind()
        attrs = (
            'maximum', 'minimum', 'value', 'prefix', 'suffix',
            'special_value_text', 'single_step', 'read_only', 'wrapping',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_value_changed(self, content):
        """ Handle the 'value_changed' action from the client widget.

        """
        self.set_guarded(value=content['value'])

