from traits.api import Interface, Str, WeakRef, Instance, List

from ..enaml_base import EnamlBase
from ..style_node import EnamlStyleNode
from ..util.trait_types import ReadOnlyConstruct


class IComponentImpl(Interface):
    """ The base Component implementation interface.

    A component implementation is responsible for listening to attributes
    on the parent and doing conversions to and from those attributes
    and values on the widget. The implementation is added as a virtual
    listener on the component with a prefix of 'parent', so any
    parent_*_changed methods will be called in response to a trait
    change on the parent. The implementation should set the traits
    on the parent (including events) when appropriate according to
    their documentation.

    Attributes
    ----------
    parent : WeakRef(Component)
        A weak referent to the parent component.

    Methods
    -------
    set_parent(parent)
        Sets the parent to the parent component. This will be called by
        the framework before the widget is to be created.

    create_widget()
        Creates the underlying toolkit widget.

    initialize_widget()
        Initializes the widget with attributes from the parent.

    layout_child_widgets()
        Add the child widgets of this component to any sizers or
        layout objects necessary to lay out the ui.

    toolkit_widget()
        Returns the toolkit specific widget.

    parent_name_changed(name)
        Called when the name trait on the parent changes.

    """
    parent = WeakRef('Component')

    def set_parent(self, parent):
        """ Sets the parent to the parent component.

        This will be called by the framework before the widget is to be
        created. Typical implementations will just assign it to the
        parent weakref. This is the first method called in the layout
        process.

        """
        raise NotImplementedError

    def create_widget(self):
        """ Creates the underlying toolkit widget. At the time this is
        called by the frameworks, the 'set_parent' method will have
        already been called. This is the second method called in the
        layout process.

        """
        raise NotImplementedError

    def initialize_widget(self):
        """ Initializes the widget with attributes from the parent. This
        is the third method called in the layout process.

        """
        raise NotImplementedError

    def initialize_style(self):
        """ Initializes the style and style handler for the widget. This
        is the fourth method called in the layout proces.

        """
        raise NotImplementedError

    def layout_child_widgets(self):
        """ Adds the child widgets (if any) to any necessary layout
        components in the ui. This is the fifth and final method called
        in the layout process.

        """
        raise NotImplementedError

    def toolkit_widget(self):
        """ Returns the toolkit specific widget being mangaged by this
        implementation object.

        """
        raise NotImplementedError

    def parent_name_changed(self, name):
        """ Called when the name on the component changes.

        """
        raise NotImplementedError


class Component(EnamlBase):
    """ The most base class of the Enaml widgets component heierarchy.

    All Enaml  widget classes should inherit from this class. This class
    is not meant to be instantiated.

    Attributes
    ----------
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

    name : Str
        The name of this element which may be used as metainfo by other
        components. Note that this is not the same as the identifier
        that can be assigned to a component as part of the enaml grammar.

    style : Instance(StyleNode)
        A protected read-only attribute that holds the component's style
        node.

    toolkit_impl : Instance(ComponentImpl)
        The toolkit specific object that implements the behavior of
        this component. This implementation object is added as a virtual
        listener for this component and maintains a weak reference to
        this component. The listeners are set up and torn down with the
        'hook_impl' and 'unhook_impl' methods. This is a protected
        attribute.

    Methods
    -------
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

    layout()
        Lay out and create the widgets for this component and it's
        children. This builds the widget tree.

    toolkit_widget()
        Returns the underlying gui toolkit widget which is being
        managed by the implemention object.

    refresh(force=False)
        Refreshes the ui tree from this point down, rebuilding children
        where necessary.

    """
    _id = Str

    _type = Str

    parent = WeakRef('Component')

    children = List(Instance('Component'))

    name = Str

    # XXX - I don't like this ReadOnlyConstruct
    style = ReadOnlyConstruct(lambda self, name: EnamlStyleNode(parent=self))

    toolkit_impl = Instance(IComponentImpl)

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

    def layout(self):
        """ Initialize and layout the component and it's children.

        In addition to running the layout process, this method calls
        hook_impl() which will add the implementation as a virtual
        listen on this instance. This method should not typically be
        called by user code.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        impl = self.toolkit_impl
        impl.set_parent(self)
        impl.create_widget()
        for child in self.children:
            child.layout()
        impl.initialize_widget()
        impl.initialize_style()
        impl.layout_child_widgets()
        self._hook_impl()

    def toolkit_widget(self):
        """ Returns the toolkit specific widget for this component.

        """
        return self.toolkit_impl.toolkit_widget()

    def refresh(self, force=False):
        """ Refreshes the layout.

        """
        pass

    def _hook_impl(self):
        """ Adds the implementation object as a listener via the
        'add_trait' method.

        """
        self.add_trait_listener(self.toolkit_impl, 'parent')


Component.protect('_id', '_type', 'parent', 'children', 'style', 'toolkit_impl')

