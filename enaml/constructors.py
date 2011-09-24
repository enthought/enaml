#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasStrictTraits, List, Instance, Tuple, Str, Interface, Either

from .widgets.component import Component
from .expressions import IExpressionDelegateFactory, IExpressionNotifierFactory


#-------------------------------------------------------------------------------
# Convienent Trait Definititions
#-------------------------------------------------------------------------------
EnamlName = Tuple(Str, Either(Str, None))

DelegateList = List(Tuple(EnamlName, Instance(IExpressionDelegateFactory)))

NotifierList = List(Tuple(EnamlName, Instance(IExpressionNotifierFactory)))

ToolkitCtorList = List(Instance('IToolkitConstructor'))


#------------------------------------------------------------------------------
# IToolkitConstructor interface
#------------------------------------------------------------------------------
class IToolkitConstructor(Interface):
    """ The IToolkitConstructor interface for toolkit constructors.

    An IToolkitConstructor object is responsible for creating a toolkit
    specific widget for a named element in an enaml file. The instance
    of the constructors are composed together to create a constructor
    tree. The root of the constructor tree is callable with context
    objects as keyword arguments, and returns an enaml.view.View object.

    Attributes
    ----------
    identifier : Str
        The unique identifier assigned to the widget (if any).
        An empty string is considered to be no id.

    type_name : Str
        The type name in use by this component that this constructor
        will create.

    delegates : DelegateList
        The list of tuples of info for delegating traits on the toolkit
        widget wrapper. The string is the name of the trait to be
        delegated and the object is an expression delegate factory which
        will create a delegate on demand.

    notifiers : NotifierList
        The list of tuples of info for setting notifiers on the widget
        wrapper. The string is the name of the trait on which we want
        notifications and the object is an expression notifier factory
        which will create a notifier on demand.

    children : ToolkitCtorList
        The list of constructor instances for any child objects
        defined for this node of the Enaml tree.

    Methods
    -------
    component()
        Imports, instantiates, and returns the toolkit specific component.

    __call__(**ctxt_objs)
        When called with context objects, should build and return
        an appropriate enaml.view.View object.

    """
    identifier = Str

    type_name = Str

    delegates = DelegateList

    notifiers = NotifierList

    children = ToolkitCtorList

    def component(self):
        """ Imports, instantiates, and returns the toolkit component.

        This method should import, instantiate, and return a toolkit
        specific component. The import is done here to delay the import
        of any gui libraries for as long as possible.

        Arguments
        ---------
        None

        Returns
        -------
        result : enaml.widgets.component.Component
            A toolkit specific component.

        """
        raise NotImplementedError

    def __call__(self, **ctxt_objs):
        """ Called with the users desired scope objects to create a View.

        This method performs the actual building of the toolkit specific
        ui tree using the provided ctxt_objs as the minimum global scope.
        The constructor is free to add items to the global scope and to
        create it's own local scopes as necessary. If a constructor is
        not a proper top level item and it's __call__ method is called,
        then it should wrap itself in an appropraite default top-level
        container, and return the view for that.

        Arguments
        ---------
        **ctxt_objs
            Items that should appear in the global namespace of the
            expressions.

        Returns
        -------
        result : enaml.view.View
            A properly instantiated View object that can be layed out and
            displayed by calling view.show()

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Base Toolkit Constructor class
#------------------------------------------------------------------------------
class BaseToolkitCtor(HasStrictTraits):
    """ A base toolkit constructor class.

    This class provides some common functionality for the majority of
    toolkit constructor classes that will need to be created. Proper
    implementations can be created by minimal subclassing of this
    class. Most subclasses will only need to implement the 'component'
    method. Selected subclasses will need to override '__call__' to do
    appropriate wrapping in default toplevel components.

    See Also
    --------
    enaml.constructors.IToolkitConstructor

    """
    identifier = Str

    type_name = Str

    delegates = DelegateList

    notifiers = NotifierList

    children = ToolkitCtorList

    #--------------------------------------------------------------------------
    # Transient traits that are reset in the cleanup method.
    #--------------------------------------------------------------------------
    # The Component instance that is created by the toolkit constructor.
    impl = Instance(Component)

    # The local namespace for this component (will contain 'self')
    local_ns = Instance(dict, ())

    # The global namespace for this component.
    # It is shared amongst all components in the view.
    global_ns = Instance(dict)

    def construct(self):
        """ Builds the tree of constructor instances. The first step
        in the construction process.

        """
        self.impl = impl = self.component()
        impl._type = self.type_name
        for child in self.children:
            child.construct()
            impl.add_child(child.impl)

    def build_ns(self, global_ns):
        """ Creates and populates the global and local namespaces,
        the initial global namespace is passed as an argument. The
        second step in the construction process.

        """
        impl = self.impl
        self.local_ns['self'] = impl
        identifier = self.identifier
        if identifier:
            if identifier in global_ns:
                msg = 'The name %s already exists in the namespace.'
                raise NameError(msg % identifier)
            else:
                global_ns[identifier] = impl
        for child in self.children:
            child.build_ns(global_ns)
        self.global_ns = global_ns

    def hook_expressions(self):
        """ Installs the expressions and notifiers on the component
        objects. The third step in the construction process.

        """
        impl = self.impl
        global_ns = self.global_ns
        local_ns = self.local_ns
        for name, delegate_factory in self.delegates:
            delegate = delegate_factory(global_ns, local_ns)
            impl.set_attribute_delegate(name, delegate)
        for name, notifier_factory in self.notifiers:
            notifier = notifier_factory(global_ns, local_ns)
            impl.add_attribute_notifier(name, notifier)
        for child in self.children:
            child.hook_expressions()

    def build_view(self):
        """ Creates a returns an enaml.view.View which will layout and
        show the ui by calling its 'show' method. The fourth step in
        the construction process.

        """
        # This avoids a circular import
        from .view import View, NamespaceProxy
        window = self.impl
        ns = NamespaceProxy(self.global_ns)
        return View(window=window, ns=ns)

    def cleanup(self):
        """ Cleans up all transitory attributes used by the constructor.
        The final step in the construction process.

        """
        self.impl = None
        self.local_ns = {}
        self.global_ns = {}
        for child in self.children:
            child.cleanup()

    def __call__(self, **ctxt_objs):
        """ Performs the construction process.

        Arguments
        ---------
        **ctxt_objs
            Objects to add to the global namespace of the view.

        Returns
        -------
        result : enaml.view.View
            A view object that can diplay the ui to the screen by
            calling its 'show' method.

        """
        self.construct()
        self.build_ns(ctxt_objs)
        self.hook_expressions()
        res = self.build_view()
        self.cleanup()
        return res

    def component(self):
        """ Creates an returns the Component instance for this
        constructor. Must be implemented by subclasses.

        """
        raise NotImplementedError

