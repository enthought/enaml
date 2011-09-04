from traits.api import (HasStrictTraits, Str, Dict, Set, WeakRef, Instance, 
                        Interface, This, ListThis)

from .expression_delegates import IExpressionDelegate, IExpressionNotifier


class IComponentImpl(Interface):

    parent = WeakRef('Component')

    def set_parent(self, parent):
        raise NotImplementedError

    def toolkit_widget(self):
        raise NotImplementedError
    
    def parent_name_changed(self, name):
        raise NotImplementedError


class Component(HasStrictTraits):
    """ The most base class of the Enaml component heierarchy. 
    
    All Enaml  widget classes should inherit from this class. This class
    is not meant to be instantiated.
    
    Attributes
    ----------
    _delegates : Dict(Str, Instance(IExpressionDelegate))
        The expression delegates currently installed on this component. 
        This is managed internally. Manipulate at your own risk.
    
    _notifiers : Set(Instance(IExpressionNotifier))
        The expression notifiers currently installed on this component. 
        This is managed internally. Manipulate at your own risk.

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

    toolkit_impl : Instance(ComponentImpl)
        The toolkit specific object that implements the behavior of 
        this component. This implementation object is added as a virtual 
        listener for this component and maintains a weak reference to 
        this component. The listeners are set up and torn down with the 
        'hook_impl' and 'unhook_impl' methods.

    Methods
    -------
    add_meta_info(meta_info)
        Add the meta info instance to this component.

    remove_meta_info(meta_info)
        Remove the meta info instance from this component.

    get_meta_handler(meta_info):
        Return the IMetaHandler for this meta_info object.

    add_child(child)
        Add a child component to this component. This will reparent
        the child.
    
    remove_child(child)
        Remove a child component from this component. This will
        unparent the child,

    replace_child(child, other_child)
        Replace child in this component with a different one. This
        will unparent the first child and reparent the second child.
    
    def set_parent(self, parent):
        Set the parent for this component to parent.

    swap_children(child, other_child)
        Swap the positions of the two children.

    hook_impl()
        Sets the toolkit_impl object as a virtual listener for this
        component instance.

    unhook_impl()
        Removes the toolkit_impl object as a virtual listener for
        this component instance.
 
    toolkit_widget()
        Returns the underlying gui toolkit widget which is being 
        managed by the implemention object.
    
    refresh(force=False)
        Refreshes the ui tree from this point down, rebuilding children 
        where necessary.

    """
    _delegates = Dict(Str, Instance(IExpressionDelegate))

    _notifiers = Set(Instance(IExpressionNotifier))

    name = Str

    parent = WeakRef(This)

    children = ListThis

    toolkit_impl = Instance(IComponentImpl)

    def delegate_attribute(self, name, delegate):
        """ Delegates the value of the attribute to the delegate.

        Call this method to intercept the value of the standard trait
        attribute and delegate that value to the given delegate.

        Arguments
        ---------
        name : string
            The name of the attribute to delegate.
        
        delegate : IExpressionDelegate
            An implementor of the IExpressionDelegate interface.

        Returns
        -------
        result : None

        """
        trait = self.trait(name)
        delegates = self._delegates
        delegate_name = '_%s_enaml_delegate' % name

        if trait is None:
            msg = '`%s` is not a proper attribute on the `%s` object.'
            raise AttributeError(msg % (name, type(self).__name__))

        if trait.type in ('property', 'event'):
            msg = 'The `%s` attr on the `%s` object cannot be delegated.'
            raise TypeError(msg % (name, type(self).__name__))

        if delegate_name in delegates:
            msg = 'The `%s` attr on the `%s` object is already delegated.'
            raise ValueError(msg % (name, type(self).__name__))
        else:
            delegates[delegate_name] = delegate

        delegate.validate_trait = trait()
        delegate.bind(self, name)

        self.add_trait(delegate_name, delegate)
        self.add_trait(name, DelegatesTo(delegate_name, 'value'))

        # Need to fire trait_added or the delegate 
        # listeners don't get hooked up properly.
        self.trait_added = name

    def notify_attribute(self, name, notifier):
        """ Adds a notifier for the given attribute name.

        Call this method to hook up an IExpressionNotifier to the
        given attribute name.

        Arguments
        ---------
        name : string
            The name of the attribute to delegate.
        
        notifier : IExpressionNotifier
            An implementor of the IExpressionNotifer interface.

        Returns
        -------
        result : None

        """
        trait = self.trait(name)
        if trait is None:
            msg = '`%s` is not a proper attribute on the `%s` object.'
            raise AttributeError(msg % (name, type(self).__name__))

        self._notifiers.add(notifier)
        notifier.bind(self, name)

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
        child.set_parent(self)
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
        child.set_parent(None)
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
        child.set_parent(None)
        other_child.set_parent(self)
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

    def set_parent(self, parent):
        """ Set the parent of this component to parent.

        The default implementation of this method simply assigns the
        parent to the .parent attribute. Subclasses may override this
        method to do any custom process before the parent is set.

        Arguments
        ---------
        parent : Component or None
            The parent Component of this component or None.

        Returns
        -------
        result : None

        """
        self.parent = parent
    
    def toolkit_widget(self):
        """ Returns the toolkit specific widget for this component.

        """
        return self.toolkit_impl.toolkit_widget()

    def parent_impl(self):
        """ Sets the parent of the toolkit implementation to self.

        """
        self.toolkit_impl.set_parent(self)
    
    def unparent_impl(self):
        """ Sets the parent of the toolkit implementation to None.

        """
        self.toolkit_impl.set_parent(None)

    def hook_impl(self):
        """ Sets the toolkit_impl object as a virtual listener for this
        component instance.

        """
        self.add_trait_listener(self.toolkit_impl, 'parent')
    
    def unhook_impl(self):
        """ Removes the toolkit_impl object as a virtual listener for
        this component instance.

        """
        self.remove_trait_listener(self.toolit_impl, 'parent')

    def refresh(self, force=False):
        """ Refreshes the layout. 

        """
        pass

