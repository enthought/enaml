#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .abstract_button import AbstractButton


class CheckBox(AbstractButton):
    """ An checkable button represented by a standard check box widget.

    Use a check box when it's necessary to toggle a boolean value
    independent of any other widgets in a group. 

    When its necessary to allow the toggling of only one value in a 
    group of values, use a group of RadioButtons or the RadioGroup
    control from the Enaml standard library.

    The interface for AbstractButton fully defines the interface for
    a CheckBox.

    """
    #: Check boxes are checkable by default.
    checkable = True

