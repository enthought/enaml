from .i_component import IComponent


class IContainer(IComponent):
    """ The base container interface. 
    
    Containers are non-visible components that are responsible for laying
    out and arranging their children.

    Methods
    -------
    add_child(child)
        Add the child component to this container.
    
    remove_child(child)
        Remove the child component from this container, but
        do not update the screen.

    replace_child(child, other_child)
        Replace child with other_child.

    children()
        An iterator of all the children.
    
    layout(parent)
        Initialize and layout the container and it's children.

    """
    def add_child(self, child):
        """ Add the child component to this container.
        
        Call this method when a child should be added to the container. 
        
        Arguments
        ---------
        child : Either(IContainer, IElement)
            The child to add to this container. The child must not
            already be in the container.

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

        Call this method when a child should be removed from the 
        container.

        Arguments
        ---------
        child : Either(IContainer, IElement)
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
        other_child.

        Arguments
        ---------
        child : Either(IContainer, IElement)
            The child being replaced. The child must be contained in 
            the container.

        other_child : Either(IContainer, IElement)
            The child taking the new place. The child must not be 
            contained in the container.

        Returns
        -------
        result : None

        Raises
        ------
        TypeError
            The child or other_child is not of the proper type.

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

    def layout(self, parent):
        """ Initialize and layout the container and it's children.

<<<<<<< wx_local
        This method should be called by the parent window during
=======
        This method should be called by the parent panel during
>>>>>>> local
        its layout process.

        Arguments
        ---------
<<<<<<< wx_local
        parent : IWindow
            The parent window of this container. The parent should 
            have already been layed out (and therefore have created 
            its internal widget) before being passed in to this method.
=======
        parent : Either(IPanel, IContainer)
            The parent of this container. The parent should have already 
            been layed out (and therefore have createdits internal widget) 
            before being passed in to this method.
>>>>>>> local

        Returns
        -------
        result : None

        Raises
        ------
        LayoutError
            Any reason the action cannot be completed.

        """
        raise NotImplementedError

