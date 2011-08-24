from traits.api import Int, Property, Instance

from .i_container import IContainer


class IStackedGroup(IContainer):
    """ A container that lays out its child containers as a stack.

    A container which lays out its children as a stack and makes only
    one child visible at a time. All children of the StackedGroup 
    must themselves be Containers.

    Attributes
    ----------
    current_index : Int
        An index which controls which child in the stack is visible.
        This is synchronized with 'current_child'.

    current_child : IContainer
        The current child container that is visible. This is 
        synchronized with 'current_index'.

    count : Property(Int)
        A read only property which returns the number of child 
        containers in the stack.
    
    Methods
    -------
    child_at(idx)
        Returns the child container at the given index.

    index_of(child)
        Returns the integer index for the given child container.

    """
    current_index = Int

    current_child = Instance(IContainer)

    count = Property(Int)

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
        TypeError
            The index is not an integer.

        IndexError
            No child corresponds to the given index.
        
        """
        raise NotImplementedError

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
        TypeError
            The child is not a Container.

        IndexError
            The child does not exist in the group.

        """
        raise NotImplementedError

