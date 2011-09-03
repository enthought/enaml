from traits.api import HasStrictTraits, Str, List, WeakRef, Instance, Interface

from .component_impl import ComponentImpl

from ..interceptors.i_interceptor import IInterceptor


class IComponentImpl(Interface):

    parent = WeakRef('Component')

    def toolkit_widget(self):
        raise NotImplementedError
    
    def parent_name_changed(self, name):
        raise NotImplementedError


class Component(HasStrictTraits):
    """ The most base class of the Enaml component heierarchy. 
    
    All Enaml abstract widget classes should inherit from this class.
    This class is not meant to be instantiated.
    
    Attributes
    ----------
    _interceptors : List(Instance(IInterceptor))
        The list of IInterceptors that are currently intercepting values
        on this component. This is managed by the framework. Use at your
        own risk.
    
    _impl : Instance(ComponentImpl)
        The toolkit specific object that implements the behavior of 
        this component. This implementation object is added as a virtual 
        listener for this component and maintains a weak reference to 
        this component. Most of the methods defined on this component
        forward directly to the implementation object.

    name : Str
        The name of this element which may be used as metainfo by other
        components. Note that this is not the same as the identifier 
        that can be assigned to a component as part of the tml grammar.
    
    parent : WeakRef(Component)
        The parent component of this component which is stored as a
        weakref to mitigate memory leak issues from reference cycles.

    children : List(Instance(Component))
        The list of children components for this component. Subclasses
        may redefine this trait to restrict which types of children
        they allow. This list should not be manipulated outside of
        the *_child(...) methods.    

    Methods
    -------
    add_meta_info(meta_info)
        Add the meta info instance to this component.

    remove_meta_info(meta_info)
        Remove the meta info instance from this component.

    get_meta_handler(meta_info):
        Return the IMetaHandler for this meta_info object.

    add_child(child)
        Add a child component to this component container.
    
    remove_child(child)
        Remove a child component from this component.

    replace_child(child, other_child)
        Replace child in this component with a different one.
    
    swap_children(child, other_child)
        Swap the positions of the two children.

    refresh(force=False)
        Refreshes the ui tree from this point down, rebuilding children 
        where necessary.

    toolkit_widget()
        Returns the underlying gui toolkit widget which is being 
        managed by the implemention object.

    """
    _interceptors = List(Instance(IInterceptor))

    _impl = Instance(IComponentImpl)
    
    name = Str

    parent = WeakRef('Component')

    children = List(Instance('Component'))

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

        """
        pass

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

        """
        pass

    def get_meta_handler(self, meta_info):
        """ Return the IMetaHandler for this meta_info object.
        
        Return the toolkit specific IMetaHandler instance for this 
        meta_info object. This may return None if the component does 
        handle this particular meta info type. The meta_info object 
        must have already been added via the add_meta_info method.

        Arguments
        ---------
        meta_info : BaseMetaInfo subclass instance
            The meta info instance for which we want the handler.

        Returns
        -------
        result : IMetaHandler or None
            The toolkit specific meta handler for this meta info
            object, or None if the component does not handle it.

        """
        pass

    def add_child(self, child):
        """ Add a child component to this component.
        
        Call this method when a child should be added to the component. 
        
        Arguments
        ---------
        child : Instance(Component)
            The child to add to the component. The child must not
            already be in the component.

        Returns
        -------
        result : None

        """
        # XXX this is O(n) but n should be small so I'm not 
        # worrying about it at the moment
        children = self.children
        if child in children:
            raise ValueError('Child %s already in children.' % child)
        self.children.append(child)
        self.refresh()

    def remove_child(self, child):
        """ Remove the child from this container.

        Call this method when a child should be removed from the 
        container.

        Arguments
        ---------
        child : Instance(Component)
            The child to remove from the container. The child
            must be contained in the container.

        Returns
        -------
        result : None

        """
        # XXX this is O(n) but n should be small so I'm not 
        # worrying about it at the moment
        try:
            self.children.remove(child)
        except ValueError:
            raise ValueError('Child %s not in children.' % child)
        self.refresh()

    def replace_child(self, child, other_child):
        """ Replace child with other_child.

        Call this method when the child should be replaced by the
        other_child.

        Arguments
        ---------
        child : Instance(Component)
            The child being replaced. The child must be contained in 
            the container.

        other_child : Instance(Component)
            The child taking the new place. The child must not be 
            contained in the container.

        Returns
        -------
        result : None

        """
        # XXX this is O(n) but n should be small so I'm not 
        # worrying about it at the moment
        children = self.children
        try:
            idx = children.index(child)
        except ValueError:
            raise ValueError('Child %s not in children.' % child)
        if other_child in children:
            raise ValueError('Child %s already in children.' % child)
        children[idx] = other_child
        self.refresh()

    def swap_children(self, child, other_child):
        """ Swap the position of two children.

        Call this method when their are two children in the container
        whose positions should be swapped.

        Arguments
        ---------
        child : Instance(Component)
            The first child in the swap. The child must be contained 
            in the container.

        other_child : Instance(Component)
            The second child in the swap. The child must be contained 
            in the container.

        Returns
        -------
        result : None

        """
        # XXX this is O(n) but n should be small so I'm not 
        # worrying about it at the moment
        children = self.children
        try:
            idx = children.index(child)
        except ValueError:
            raise ValueError('Child %s not in children.' % child)
        try:
            other_idx = children.index(other_child)
        except ValueError:
            raise ValueError('Child %s not in children.' % other_child)
        children[idx] = other_child
        children[other_idx] = child
        self.refresh()

    def toolkit_widget(self):
        return self._impl.toolkit_widget()
            
    def _hook_impl(self):
        self.add_trait_listener(self._impl, 'parent')
    
    def _unhook_impl(self):
        self.remove_trait_listener(self._impl, 'parent')

    def refresh(self, force=False):
        raise NotImplementedError




