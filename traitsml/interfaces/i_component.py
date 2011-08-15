from traits.api import Interface, Str, Any


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

    widget : Any
        The underlying toolkit widget being managed by the component.

    Methods
    -------
    add_meta_object(meta_obj)
        Add the MetaInfo instance to this component.

    remove_meta_object(meta_obj)
        Remove the MetaInfo instance from this component.

    """
    name = Str

    widget = Any

    def add_meta_obj(self, meta_obj):
        """ Add the MetaInfo object to this component.

        MetaInfo objects supply additional meta information about an 
        object (such as styling and layout info) to various other parts
        of the TraitsML object tree.

        Arguments
        ---------
        meta_obj : MetaInfo
            The MetaInfo instance to add to this component.

        Returns
        -------
        result : None

        Raises
        ------
        TypeError
            The meta_obj is not a MetaInfo instance.
        
        ComponentError
            Any other reason the operation cannot be completed.

        """
        raise NotImplementedError

    def remove_meta_obj(self, meta_obj):
        """ Remove the MetaInfo object from this component.

        Arguments
        ---------
        meta_obj : MetaInfo
            The MetaInfo instance to remove from this component. It
            must have been previously added via 'add_meta_obj'.

        Returns
        -------
        result : None

        Raises
        ------
        TypeError
            The meta_obj is not a MetaInfo instance.

        ValueError
            The meta_obj was not previously added via 'add_meta_obj'.

        ComponentError
            Any oher reason the operation cannot be completed.

        """
        raise NotImplementedError

