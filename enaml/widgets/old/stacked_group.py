#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Int, Property, Instance, List

from .container import IContainerImpl, Container

# XXX - punt on this for now
class IStackedGroupImpl(IContainerImpl):

    def parent_current_index_changed(self, current_index):
        raise NotImplementedError


class StackedGroup(Container):
    """ A container that lays out its child containers as a stack.

    A container which lays out its children as a stack and makes only
    one child visible at a time. All children of the StackedGroup
    must themselves be Containers.

    Attributes
    ----------
    current_index : Int
        An index which controls which child in the stack is visible.
        This is synchronized with 'current_child'.

    count : Property(Int)
        A read only property which returns the number of children
        in the stack.

    Methods
    -------
    child_at(idx)
        Returns the child container at the given index.

    index_of(child)
        Returns the integer index for the given child container.

    """
    current_index = Int

    count = Property(Int, depends_on='children')

    children = List(Container)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IStackedGroupImpl)

    def child_at(self, idx):
        """ Returns the child container at the given index.

        Arguments
        ---------
        idx : int
            The zero based index to use to lookup the child container.
            It may be negative, in which case the lookup will be
            from the end of the stack.

        Returns
        -------
        result : IContainer
            The child container at the given index.

        Raises
        ------
        TypeError :
            The index is not an integer.

        IndexError :
            No child corresponds to the given index.

        """
        return self.toolkit_impl.child_at(idx)

    def index_of(self, child):
        """ Returns the index corresponding to the given child container.

        Arguments
        ---------
        child : IContainer
            The child container to lookup.

        Returns
        -------
        result : int
            The index of the given child container.

        Raises
        ------
        TypeError :
            The child is not a Container.

        IndexError :
            The child does not exist in the group.

        """
        return self.toolkit_impl.index_of(child)

    def _get_count(self):
        return len(self.children)


StackedGroup.protect('count')

