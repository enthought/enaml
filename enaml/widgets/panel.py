from .component import Component


class Panel(Component):
    """ The base panel wiget.

    Panel widgets hold a container of components and arrange them on an
    otherwise empty widget.

    Methods
    -------
    set_container(container)
        Set the container of child widgets and/or containers for
        this window.

    get_container(container)
        Get the container of child widgets and/or containers for 
        this panel.

    layout(parent)
        Initialize and layout the panel and it's children.

    """
    def set_container(self, container):
        """ Set the container of children for this panel.
        
        Calling this method more than once will replace the previous
        container with the provided container.

        Arguments
        ---------
        container : IContainer
            The container of child widgets and/or containers for
            this window.

        Returns
        -------
        None

        Raises
        ------
        None

        """
        raise NotImplementedError
        
    def get_container(self):
        """ Return the container of children for this panel.

        Call this method to retrieve the container previously 
        set with set_container.

        Arguments
        ---------
        None

        Returns
        -------
        result : IContainer or None
            Returns the conainter set on this window if one is set.

        Raises
        ------
        None

        """
        raise NotImplementedError

    def layout(self, parent):
        """ Initialize and layout the panel and it's children.

        Call this method after the object tree has been built in order
        to create and arrange the underlying widgets. It can be called 
        again at a later time in order to rebuild the view.

        Arguments
        ---------
        parent : IComponent or None
            The parent component of this window. Pass None if there is
            not parent. The parent should have already been layed out 
            (and therefore have created its internal widget) before being 
            passed into this method.

        Returns
        -------
        result : None

        Raises
        ------
        LayoutError
            Any reason the action cannot be completed.

        """
        raise NotImplementedError

