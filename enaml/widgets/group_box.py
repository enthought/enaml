#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Instance

from .container import IContainerImpl, Container


class IGroupBoxImpl(IContainerImpl):

    def parent_checkable_changed(self):
        raise NotImplementedError
    
    def parent_checked_changed(self):
        raise NotImplementedError
    
    def parent_title_changed(self):
        raise NotImplementedError


class GroupBox(Container):
    """ A container that can draw a border around its children.

    The GroupBox can draw an optional border around its child widgets.
    A GroupBox can also be checkable which will enable and disable its 
    children. The children of a GroupBox are layed out vertically, if
    this is not the desired behavior, use another container as the
    only child of the GroupBox which arranges the chilren as necessary.

    Attributes
    ----------
    checkable : Bool
        Whether or not the group has a check box.

    checked : Bool
        If checkable, whether or not the box is checked. If the 
        group box is checkable and the box is unchecked, then all 
        of the children in the group will be disabled.

    title: Str
        The title of the group box.

    """
    checkable = Bool

    checked = Bool

    title = Str

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IGroupBoxImpl)

    