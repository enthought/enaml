from .i_component import IComponent


class IContainer(IComponent):
    """ The base container interface. 
    
    Containers are non-visible components that are responsible for laying
    out and arranging their children.

    Methods
    -------
    add_child(child)
        Add the child component to this container. Do not layout.
    
    remove_child(child)
        Remove the child component from this container, but
        do not update the screen.         

    replace_child(child, other_child)
        Replace child with other_child, but do not update the screen.

    rearrange()
        Rearrange the childrent according to the current layout.
    
    children()
        An iterator of all the children.

    """

    def add_child(self, child):
        """ Add the child component to this container.
        
        Call this method when a child should be added to the container. 
        The container will not visibly arrange the children until the
        'layout' method is called and will continue to function
        as normal until that time.

        Arguments
        ---------
        child : IComponent
            The child to add to this container.

        Returns
        -------
        result : None

        Raises
        ------
        TypeError
            The child is not an instance of IComponent.

        ContainerError
            Any other reason the action cannot be completed.

        """
        raise NotImplementedError

    def remove_child(self, child):
        """ Remove the child from this container.

        Call this method when a child should be remove from the 
        container. The container will not visibly arrange the 
        children until the 'layout' method is called and will 
        continue to function as normal until that time.

        Arguments
        ---------
        child : IComponent
            The child to remove from the container. The child
            must be contained in the container.

        Returns
        -------
        result : None

        Raises
        ------
        TypeError
            The child is not an instance of IComponent.

        ValueError
            The child is not contained in the container.

        ContainerError
            Any other reason the action cannot be completed.

        """
        raise NotImplementedError

    def replace_child(self, child, other_child):
        """ Replace child with other_child.

        Call this method when the child should be replaced by the
        other_child. The container will not visibly arrange the 
        children until the 'layout' method is called and will
        continue to function as normal until that time.

        Arguments
        ---------
        child : IComponent
            The child being replaced. The child be contained in the 
            container.

        other_child : IComponent
            The child taking the new place. The child must not be 
            contained in the container.

        Returns
        -------
        result : None

        Raises
        ------
        TypeError
            The child or other_child is not an instance of IComponent.

        ValueError
            The child is not contained in the container or other_child
            is contained in the container.

        ContainerError
            Any other reason the action cannot be completed.

        Notes
        -----
        To replace a child with one that already exists in the container,
        call 'remove_child' followed by 'replace_child'.

        """
        raise NotImplementedError

    def rearrange(self):
        """  Rearrange the childrent according to the current layout.

        Call this method after all child manipulations have been 
        completed and the children should be visibly rearranged.
        Calling this is only necessary when changing children
        *after* the ui has already been made visible.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        LayoutError
            Any reason the action cannot be completed.

        """
        raise NotImplementedError

    def children(self):
        """ An iterator of the contained children.

        Iterate over the results of this method to access all the
        children of the container.

        Arguments
        ---------
        None
        
        Returns
        -------
        result : iter
            An iterator of the children contained in the container.

        Raises
        ------
        None
        
        Notes
        -----
        There is no guarantee to the accuracy of the itertor if the
        children of the container are modified during iteration.

        """
        raise NotImplementedError

