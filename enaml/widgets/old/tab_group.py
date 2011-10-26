#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Event, Instance

from .stacked_group import IStackedGroupImpl, StackedGroup

# XXX - punt on this for now
class ITabGroupImpl(IStackedGroupImpl):

    def parent_movable_changed(self, movable):
        raise NotImplementedError


class TabGroup(StackedGroup):
    """ A container that lays out its child containers as a notebook.

    A container which lays out its children as a notebook and makes
    only one child visible at a time. All children of the TabGroup
    must themselves be Containers. The names of the tabs will be
    derive from the 'name' attributes of the children.

    Attributes
    ----------
    movable : Bool
        If True, then the notebook pages can be rearranged by dragging
        the tabs. If tabs are reordered then the integer indexes
        corresponding to the children will also be reordered.

    reordered : Event
        Fired when the notebook tabs are reordered by the user,
        provided that 'movable' is set to True. The args object
        will contain the (from, to) index of tab movement.

    """
    movable = Bool

    reordered = Event

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ITabGroupImpl)


TabGroup.protect('reordered')

