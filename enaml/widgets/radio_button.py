#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .abstract_button import AbstractButton


class RadioButton(AbstractButton):
    """ An exclusive checkable button represented by a standard radio
    button widget. 

    Use a radio button to toggle the value of a boolean field. For a 
    group of radio buttons with the same widget parent, only one radio 
    button may be selected at a time. This makes groups of radio buttons 
    useful for selecting amongst a discrete set of values. For multiple 
    groups of independent radio buttons, place each group of buttons
    in their own Container.

    The interface for AbstractButton fully defines the interface for
    a RadioButton.

    """
    #: Radio buttons are checkable by default.
    checkable = True

