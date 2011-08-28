from traits.api import Interface, Str


class IComponent(Interface):
    """ The most base class of the TraitsML component heierarchy. 
    
    All TraitsML ui interface classes should inherit from this class. A 
    TraitsML component interface specifies the attributes and minimum 
    methods required of any backend implementation. This class is 
    not meant to be instantiated.
    
    Attributes
    ----------
    name : Str
        The name of this element which may be used as metainfo by other
        components. Note that this is not the same as the identifier 
        that can be assigned to a component as part of the tml grammar.

    Methods
    -------
    add_meta_info(meta_info)
        Add the meta info instance to this component.

    remove_meta_info(meta_info)
        Remove the meta info instance from this component.

    get_meta_handler(meta_info):
        Return the IMetaHandler for this meta_info object.

    toolkit_widget()
        Returns the underlying toolkit widget which is being managed
        by the component.

    parent()
        Returns the logical parent of this component or None.
        
    """
    name = Str

    def add_meta_info(self, meta_info, autohook=True):
        """ Add the meta info object to this component.

        Meta info objects supply additional meta information about an 
        object (such as styling and geometry info) to various other parts
        of the TraitsML object tree.

        Arguments
        ---------
        meta_info : BaseMetaInfo subclass instance
            The meta info instance to add to this component.

        autohook : bool, optional
            Whether or not to hook the handler immediately. Defaults
            to True. If False, the hook() method on the handler will 
            need to be called before it will perform any work.
            
        Returns
        -------
        result : None

        Raises
        ------
        TraitError
            The meta_info is not a BaseMetaInfo instance.
        
        ValueError
            The meta_info instance has already been added.

        ComponentError
            Any other reason the operation cannot be completed.

        """
        raise NotImplementedError

    def remove_meta_info(self, meta_info):
        """ Remove the meta info object from this component.

        Arguments
        ---------
        meta_info : BaseMetaInfo subclass instance
            The meta info instance to remove from this component. 
            It must have been previously added via 'add_meta_info'.

        Returns
        -------
        result : None

        Raises
        ------
        TraitError
            The meta_info is not a BaseMetaInfo instance.

        ValueError
            The meta_info was not previously added via 'add_meta_info'.

        ComponentError
            Any oher reason the operation cannot be completed.

        """
        raise NotImplementedError

    def get_meta_handler(self, meta_info):
        """ Return the IMetaHandler for this meta_info object.
        
        Return the toolkit specific IMetaHandler instance for
        this meta_info object. This may return None if the 
        component does handle this particular meta info type.

        The meta_info object must have already been added via
        the add_meta_info method.

        Arguments
        ---------
        meta_info : BaseMetaInfo subclass instance
            The meta info instance for which we want the handler.

        Returns
        -------
        result : IMetaHandler or None
            The toolkit specific meta handler for this meta info
            object, or None if the component does not handle it.
        
        Raises
        ------
        ValueError
            The meta_info was not previously added via add_meta_info.

        """
        raise NotImplementedError

    def toolkit_widget(self):
        """ Returns the toolkit specific widget for this component.

        Call this method to retrieve the toolkit specific widget
        for this component. Note that the toolkit widget may not
        be created before the 'layout' method on the top level
        window is called. In that case, this method will return
        None.

        Arguments
        ---------
        None

        Returns
        -------
        result : widget or None
            The toolkit specific widget, or None if the widget has not 
            yet been created.

        """
        raise NotImplementedError

    def parent(self):
        """ Returns the logical parent for this component or None.

        Returns the logical parent for this component or None if
        it is top-level. The component should take care to not
        create reference cycles to the parent and will likely want
        to keep an internal weakref to the parent, only creating
        the strong ref upon request.

        Arguments
        ---------
        None

        Returns
        -------
        result : IComponent or None
            The parent component if this component is not top-level.

        """
        raise NotImplementedError

