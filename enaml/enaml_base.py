from traits.api import HasStrictTraits, Instance, Dict, Str, Set, List, WeakRef, DelegatesTo

from .expressions import IExpressionDelegate, IExpressionNotifier
from .util.decorators import protected


@protected('_delegates', '_notifiers', '_id', '_type', 'parent', 'children')
class EnamlBase(HasStrictTraits):
    """ The most base class of types used in Enaml source files.

    Attributes
    ----------
    _delegates : Dict(Str, Instance(IExpressionDelegate))
        The expression delegates currently installed on this component. 
        This is a protected attribute and is managed internally. 
        Manipulate at your own risk.
    
    _notifiers : Set(Instance(IExpressionNotifier))
        The expression notifiers currently installed on this component. 
        This is a protected attribute and is managed internally. 
        Manipulate at your own risk.
    
    _id : Str
        The identifier assigned to this element in the enaml source code.
        Note that if you change this, you will likely break things. This
        is a protected attribute.

    _type : Str
        The type name this component is using in the enaml source code.
        This is a protected attribute.

    parent : WeakRef(EnamlBase)
        The parent object which is stored as a weakref to mitigate memory 
        leak issues from reference cycles. This is a protected attribute.

    children : List(Instance(EnamlBase))
        The list of children components for this component. Subclasses
        may redefine this trait to restrict which types of children
        they allow. This list should not be manipulated outside of
        the *_child(...) methods. This is a protected attribute.

    Methods
    -------
    set_attribute_delegate(name, delegate)
        Delegates the value of the attribute to the delegate.

    add_attribute_notifier(name, notifier)
        Adds a notifier for the given attribute name.

    add_child(child)
        Add a child component to this component. This will reparent
        the child.
    
    remove_child(child)
        Remove a child component from this component. This will
        unparent the child,

    replace_child(child, other_child)
        Replace child in this component with a different one. This
        will unparent the first child and reparent the second child.
    
    swap_children(child, other_child)
        Swap the positions of the two children.

    set_parent(self, parent):
        Set the parent for this component to parent.
    
    """
    _delegates = Dict(Str, Instance(IExpressionDelegate))

    _notifiers = Set(Instance(IExpressionNotifier))

    _id = Str

    _type = Str

    parent = WeakRef('EnamlBase')

    children = List(Instance('EnamlBase'))

    def _set_extended_delegate(self, name, delegate):
        root, attr = name.split('.')
        root_obj = getattr(self, root)
        if isinstance(root_obj, EnamlBase):
            root_obj.set_attribute_delegate(attr, delegate)

    def _set_extended_notifier(self, name, notifier):
        root, attr = name.split('.')
        root_obj = getattr(self, root)
        if isinstance(root_obj, EnamlBase):
            root_obj.set_attribute_notifier(attr, notifier)

    def set_attribute_delegate(self, name, delegate):
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
        if '.' in name:
            self._set_extended_delegate(name, delegate)
            return

        if name in self.__protected__:
            msg = ('The `%s` attribute of the `%s` object is protected '
                   'and cannot be used in an Enaml expression.')
            raise AttributeError(msg % (name, type(self).__name__))
        
        trait = self.trait(name)
        delegates = self._delegates
        delegate_name = '_%s_enaml_delegate' % name

        if trait is None:
            import pdb; pdb.set_trace()
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

        delegate.bind(self, name, trait())

        self.add_trait(delegate_name, delegate)
        self.add_trait(name, DelegatesTo(delegate_name, 'value'))

        # Need to fire trait_added or the delegate 
        # listeners don't get hooked up properly.
        self.trait_added = name

    def add_attribute_notifier(self, name, notifier):
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
        if '.' in name:
            self._set_extended_notifier(name, notifier)
            return

        if name in self.__protected__:
            msg = ('The `%s` attribute of the `%s` object is protected '
                   'and cannot be used in an Enaml expression.')
            raise AttributeError(msg % (name, type(self).__name__))

        trait = self.trait(name)
        if trait is None:
            msg = '`%s` is not a proper attribute on the `%s` object.'
            raise AttributeError(msg % (name, type(self).__name__))

        self._notifiers.add(notifier)
        notifier.bind(self, name)

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

