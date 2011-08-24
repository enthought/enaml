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
        Add the IMetaInfo instance to this component.

    remove_meta_info(meta_info)
        Remove the IMetaInfo instance from this component.

    toolkit_widget()
        Returns the underlying toolkit widget which is being managed
        by the component.

    """
    name = Str

    def add_meta_info(self, meta_info):
        """ Add the IMetaInfo object to this component.

        IMetaInfo objects supply additional meta information about an 
        object (such as styling and geometry info) to various other parts
        of the TraitsML object tree.

        Arguments
        ---------
        meta_info : IMetaInfo
            The IMetaInfo instance to add to this component.

        Returns
        -------
        result : None

        Raises
        ------
        TraitError
            The meta_info is not an IMetaInfo instance.
        
        ValueError
            The meta_info instance has already been added.

        ComponentError
            Any other reason the operation cannot be completed.

        """
        raise NotImplementedError

    def remove_meta_info(self, meta_info):
        """ Remove the IMetaInfo object from this component.

        Arguments
        ---------
        meta_info : IMetaInfo
            The IMetaInfo instance to remove from this component. It
            must have been previously added via 'add_meta_info'.

        Returns
        -------
        result : None

        Raises
        ------
        TraitError
            The meta_info is not an IMetaInfo instance.

        ValueError
            The meta_info was not previously added via 'add_meta_info'.

        ComponentError
            Any oher reason the operation cannot be completed.

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
            Returns a toolkit specific widget, or None if the widget
            has not yet been created.

        """
        raise NotImplementedError
  
