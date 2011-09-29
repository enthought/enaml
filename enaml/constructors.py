#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (Any, HasStrictTraits, List, Instance, Str, Interface, 
                        implements)

from .expressions import IExpressionDelegateFactory, IExpressionNotifierFactory


#------------------------------------------------------------------------------
# Expression Binders
#------------------------------------------------------------------------------
class ExpressionBinder(HasStrictTraits):

    _name = Str

    _id_scope = Instance(dict)

    _base_scope = Instance(dict)

    _global_scope = Instance(dict)

    def __init__(self, name, id_scope, base_scope, global_scope):
        super(HasStrictTraits, self).__init__()
        self._name = name
        self._id_scope = id_scope
        self._base_scope = base_scope
        self._global_scope = global_scope

    def build_local_scope(self, impl):
        local_scope = {}
        local_scope.update(self._id_scope)
        local_scope.update(self._base_scope)
        local_scope['self'] = impl
        return local_scope

    def bind(self, impl):
        raise NotImplementedError


class DelegateBinder(ExpressionBinder):

    _delegate_factory = Instance(IExpressionDelegateFactory)

    def __init__(self, delegate_factory, *args):
        super(DelegateBinder, self).__init__(*args)
        self._delegate_factory = delegate_factory

    
    def bind(self, impl):
        global_scope = self._global_scope
        local_scope = self.build_local_scope(impl)
        delegate = self._delegate_factory(global_scope, local_scope)
        impl.set_attribute_delegate(self._name, delegate)


class NotifierBinder(ExpressionBinder):

    _notifier_factory = Instance(IExpressionNotifierFactory)

    def __init__(self, notifier_factory, *args):
        super(NotifierBinder, self).__init__(*args)
        self._notifier_factory = notifier_factory

    def bind(self, impl):
        global_scope = self._global_scope
        local_scope = self.build_local_scope(impl)
        notifier = self._notifier_factory(global_scope, local_scope)
        impl.add_attribute_notifier(self._name, notifier)


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

    Methods
    -------
    __init__(identifer)
        Instantiates a constructor with the given identifier.

    __call__(global_ns, ctxt_objs)
        When called with the global namespace dict and a dictionary of 
        context objects, should build and return an appropriate enaml
        ui object.
            
    add_child(child_ctor)
        Adds a child constructor instance to this parent constructor.

    add_expression_binder(binder)
        Document me

    component()
        A classmethod that assembles and returns an enaml component.
    
    component_class()
        A classmethod which imports and returns the component class.

    impl_class()
        A classmethod which imports and returns the implementation class.

    type_name()
        A classmethod which returns the string name of the component
        as used in enaml source code.

    """
    def __init__(self, identifier):
        """ Initialize a toolkit constructor instance.

        Parameters
        ----------
        identifier : string
            The enaml identifier to be used when creating the underlying
            enaml component. An empty string means no identifier.
        
        """
        raise NotImplementedError

    def __call__(self, module_dict, scope_dict):
        """ Called with the users desired scope objects to create a View.

        This method performs the actual building of the toolkit specific
        ui tree using the provided scope objects.

        Arguments
        ---------
        module_dict : dict
            The dictionary of the module in which we're executing.
            This will be used as the global scope.
        
        scope_dict : dict
            A dictionary which maps the scope objects being passed
            into the view. These items will be added to the local
            scope of every expression.

        Returns
        -------
        result : (Component, dict)
            The root component object and a dictionary which contains
            all of the named objects in the scope of the view.

        """
        raise NotImplementedError

    def add_child(self, child_ctor):
        """ Adds a child constructor instance to this parent constructor.

        Parameters
        ----------
        child_ctor : Instance(IToolkitConstructor)
            The child constructor instance.

        """
        raise NotImplementedError
    
    def add_expression_binder(self, binder):
        """ Document me.
        """
        raise NotImplementedError

    @classmethod
    def component(cls):
        """ Instantiates, and returns the toolkit component.

        This method should call the component_class and impl_class
        methods to retrieve the two pieces necessary to create 
        a full enaml component.

        Parameters
        ----------
        None

        Returns
        -------
        result : enaml.widgets.component.Component
            A toolkit specific component.

        """
        raise NotImplementedError

    @classmethod
    def component_class(cls):
        """ Imports and returns the class which creates the component
        for this constructor. Imports should be done within this method
        to make things as lazy and efficient as possible.

        """
        raise NotImplementedError

    @classmethod
    def impl_class(cls):
        """ Imports and returns the class which creates the toolkit widget
        for this constructor. Imports should be done within this method
        to make things as lazy and efficient as possible.

        """
        raise NotImplementedError

    @classmethod
    def type_name(cls):
        """ Returns the string type name of the component as used in enaml
        source code.
        
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
    _identifier = Str

    _children = List(Instance(IToolkitConstructor))

    _expression_binders = List(Instance(ExpressionBinder))

    def __init__(self, identifier):
        """ Initialize a toolkit constructor instance.

        Parameters
        ----------
        identifier : string
            The enaml identifier to be used when creating the underlying
            enaml component. An empty string means no identifier.
        
        """
        super(BaseToolkitCtor, self).__init__()
        self._identifier = identifier

    def __call__(self, id_scope):
        """ Called with the users desired scope objects to create a View.

        This method performs the actual building of the toolkit specific
        ui tree using the provided scope objects.

        Arguments
        ---------
        module_dict : dict
            The dictionary of the module in which we're executing.
            This will be used as the global scope.
        
        scope_dict : dict
            A dictionary which maps the scope objects being passed
            into the view. These items will be added to the local
            scope of every expression.

        Returns
        -------
        result : (Component, dict)
            The root component object and a dictionary which contains
            all of the named objects in the scope of the view.

        """
        impl_map = {}
        impl = self.construct(impl_map, id_scope)
        self.bind_expressions(impl_map)
        return impl

    def construct(self, impl_map, id_scope):
        """ Builds the tree of constructor instances. The first step
        in the construction process.

        """
        impl = self.component()
        impl.type = self.type_name()
        impl.id = impl_id = self._identifier

        impl_map[self] = impl
        if impl_id:
            id_scope[impl_id] = impl

        for child in self._children:
            impl.add_child(child.construct(impl_map, id_scope))

        return impl

    def bind_expressions(self, impl_map):
        """ Installs the expressions and notifiers on the component
        objects. The third step in the construction process.

        """
        impl = impl_map[self]
        for binder in self._expression_binders:
            binder.bind(impl)
        for child in self._children:
            child.bind_expressions(impl_map)

    def add_child(self, child_ctor):
        """ Adds a child constructor instance to this parent constructor.

        Parameters
        ----------
        child_ctor : Instance(IToolkitConstructor)
            The child constructor instance.

        """
        self._children.append(child_ctor)
    
    def add_expression_binder(self, binder):
        """ document me

        """
        self._expression_binders.append(binder)

    @classmethod
    def component(cls):
        """ Creates an returns the Component instance for this
        constructor. Must be implemented by subclasses.

        """
        component_class = cls.component_class()
        impl_class = cls.impl_class()
        return component_class(toolkit_impl=impl_class())

    @classmethod
    def component_class(cls):
        """ Gets and returns the component class for this constructor.
        Must be implemented by subclasses.

        """
        raise NotImplementedError

    @classmethod
    def impl_class(cls):
        """ Gets and returns the toolkit implementation class for this 
        component created by this constructor. Must be implemented by 
        subclasses.

        """
        raise NotImplementedError
    
    @classmethod
    def type_name(cls):
        """ Returns the string type name of the component as used in enaml
        source code. Must be implemented by subclasses.
        
        """
        raise NotImplementedError


class DefnCallCtorProxy(BaseToolkitCtor):
    """ A BaseToolkitCtor subclass which will link up a sub component
    that was generated by a call to a factory.

    """
    _impl = Any

    _id_scope = Instance(dict)

    def __init__(self, impl, id_scope):
        super(DefnCallCtorProxy, self).__init__('')
        self._impl = impl
        self._id_scope = id_scope

    def __call__(self, id_scope):
        id_scope.update(self._id_scope)
        return self._impl

    def construct(self, impl_map, id_scope):
        impl_map[self] = self._impl
        return self._impl

    def bind_expressions(self, impl_map):
        pass


#------------------------------------------------------------------------------
# Base Constructor variants
#------------------------------------------------------------------------------
class ImportCtor(BaseToolkitCtor):
    """ A BaseToolkitCtor derived constructor that imports the proper
    classes based on strings defined as class attributes. The type
    name of the component is also determined by these strings.

    """
    implements(IToolkitConstructor)

    comp = ''

    impl = ''

    @classmethod
    def _resolve_import(cls, spec):
        path, name = spec.split(':')
        fromlist = path.split('.')
        mod = __import__(path, fromlist=fromlist)
        return getattr(mod, name)

    @classmethod
    def component_class(cls):
        comp = cls.comp
        if not comp:
            msg = 'A comp string must be supplied for `%s`.' % cls.__name__
            raise NotImplementedError(msg)
        return cls._resolve_import(comp)
    
    @classmethod
    def impl_class(cls):
        impl = cls.impl
        if not impl:
            msg = 'An impl string must be supplied for `%s`.' % cls.__name__
            raise NotImplementedError(msg)
        return cls._resolve_import(impl)

    @classmethod
    def type_name(cls):
        comp = cls.comp
        if not comp:
            msg = 'A comp string must be supplied for `%s`.' % cls.__name__
            raise NotImplementedError(msg)
        return comp.split(':')[-1]


