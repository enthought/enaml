#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import ast
from abc import ABCMeta, abstractmethod
from collections import namedtuple
import weakref

from traits.api import HasTraits, TraitType, TraitChangeNotifyWrapper

from .parsing.analyzer import AttributeVisitor


#------------------------------------------------------------------------------
# Expression default trait
#------------------------------------------------------------------------------
class ExpressionDefaultTrait(TraitType):
    """ A custom trait type that handles initializing a component
    trait attribute with a value computed from an expression binder.
    This is meant for use with subclasses of EnamlBase. It should 
    be added as an instance trait and will remove itself upon the 
    first call to 'get' or 'set'

    """
    def __init__(self, expression):
        """ Initialize a binder default trait.

        Parameters
        ----------
        expression : Instance(IExpressionBinder)
            An instance of an expression binder that will give use the 
            default value.

        """
        super(ExpressionDefaultTrait, self).__init__()
        self.expression = expression

    def rebind(self, obj, name, notifier):
        """ Rebinds a trait notifier by reconstructing the handler and 
        calling on_trait_change to create the new notifier. Currently
        only handles TraitChangeNotifyWrappers.

        """
        if isinstance(notifier, TraitChangeNotifyWrapper):
            call_method = notifier.call_method
            if call_method.startswith('call_'):
                handler = notifier.handler
            elif call_method.startswith('rebind_call_'):
                # The handler object is stored as a weakref
                handler_obj = notifier.object()
                if handler_obj is None:
                    return
                handler_name = notifier.name
                handler = getattr(handler_obj, handler_name)
            else:
                msg = 'unknown call method `%s`' % call_method
                raise ValueError(msg)
            obj.on_trait_change(handler, name)

    def remove(self, obj, name):
        """ Removes the instance trait 'name' from the given object.
        Any notifiers on the instance trait will be applied to the
        class trait via the 'rebind' method.

        """
        instance_trait = obj._instance_traits().get(name)
        if instance_trait is not None:
            obj.remove_trait(name)
            instance_notifiers = instance_trait._notifiers(0)
            if instance_notifiers is not None:
                class_trait = obj.trait(name)
                if class_trait is not None:
                    for notifier in instance_notifiers:
                        self.rebind(obj, name, notifier)

    def get(self, obj, name):
        """ Called to get the value of the trait. 

        Calling this method removes this trait from the object, evaluates 
        the expression, then performs a setattr followed by a getattr to 
        mimick a user performing the operation and to ensure safety when
        operating on delegates or properties.

        """
        self.remove(obj, name)
        val = self.expression.eval_expression()
        setattr(obj, name, val)
        return getattr(obj, name)

    def set(self, obj, name, val):
        """ Called to set the value of the trait. 

        Calling this method removes this trait from the object, then
        performs a setattr with the value. This operations ensures 
        safety when operating on delegates or properties.

        """
        self.remove(obj, name)
        setattr(obj, name, val)


#------------------------------------------------------------------------------
# Custom mapping type for namespace type checking
#------------------------------------------------------------------------------
class MappingType(object):
    """ An abstract class used for type checking on instances to ensure
    that they provide a __getitem__ and __setitem__ method.

    """
    __metaclass__ = ABCMeta

    @classmethod
    def __subclasshook__(cls, C):
        """ Returns True if the class has a __getitem__ and __setitem__
        method. Otherwise, returns NotImplemented.

        """
        if cls is MappingType:
            if hasattr(C, '__getitem__') and hasattr(C, '__setitem__'):
                return True
        return NotImplemented


#------------------------------------------------------------------------------
# Express Locals
#------------------------------------------------------------------------------
class ExpressionLocals(object):
    """ A mapping object that will first look in the provided overrides,
    then in the given locals mapping, and finally in the attribute space 
    of the given object.
    
    Notes
    -----
    Setting items on this object will delegate the operation to the
    provided locals mapping.

    Strong references are kept to all objects passed to the constructor,
    so care should be taken in managing the lifetime of these scope
    objects since their use is likely to create reference cycles.
    (It's probably best to create these objects on-the-fly when needed)

    """
    __slots__ = ('local_ns', 'obj', 'overrides')

    def __init__(self, local_ns, obj, overrides):
        """ Initialize an expression locals instance.

        Parameters
        ----------
        local_ns : dict
            The locals dict to check before checking the attribute space
            of the given object.
        
        obj : object
            The python object on which to attempt the getattr.
        
        overrides : dict
            Objects that should take complete precedent in the scope
            lookup. Note this is a dict instead of **overrides, so that
            'self' can be added to the namespace. If we didn't do this,
            'self' would clash with this method definition.

        """
        self.local_ns = local_ns
        self.obj = obj
        self.overrides = overrides
    
    def __getitem__(self, name):
        """ Lookup an item from the namespace.

        Returns the named item from the namespace by first looking in 
        the overrides, then the provided locals namespace, and finally
        the attribute space of the object. If the value is not found,
        a KeyError is raised.

        Parameters
        ----------
        name : string
            The name that should be looked up in the namespace.

        Returns
        -------
        result : object
            The value associated with the name, if found.

        """
        try:
            res = self.overrides[name]
        except KeyError:
            try:
                res = self.local_ns[name]
            except KeyError:
                try:
                    res = getattr(self.obj, name)
                except AttributeError:
                    raise KeyError(name)
        return res

    def __setitem__(self, name, val):
        """ Set the value in the local namespace.

        This operation delegates the setting to the local namespace that
        was provided during instantiation.

        Paramters
        ---------
        name : string
            The name to set in the namespace.
        
        val : object
            The value to set in the namespace.
        
        """
        self.local_ns[name] = val


#------------------------------------------------------------------------------
# Abstract Expression
#------------------------------------------------------------------------------
class AbstractExpression(object):
    
    __metaclass__ = ABCMeta
    
    __slots__ = ('obj_ref', 'attr_name', 'py_ast', 'code', 'globals_f', 
                 'locals_f', '__weakref__')
    
    def __init__(self, obj, attr_name, py_ast, code, globals_f, locals_f):
        """ Initializes and expression object.

        Parameters
        ----------
        obj : HasTraits instance
            The HasTraits instance to which we are binding the expression.
        
        attr_name : string
            The attribute name on `obj` to which this expression is bound.
        
        py_ast : ast.Expression instance
            An ast.Expression node instance.
        
        code : types.CodeType object
            The compile code object for the provided ast node.
        
        globals_f : callable
            A callable that will return the global namespace for the
            expression.
        
        locals_f : callable
            A callable that will return the local namespace for the
            expression. (excluding 'self' and 'self' attributes)

        """
        # We keep a weakref to obj to avoid ref cycles
        self.obj_ref = weakref.ref(obj)
        self.attr_name = attr_name
        self.py_ast = py_ast
        self.code = code
        self.globals_f = globals_f
        self.locals_f = locals_f
    
    @property
    def obj(self):
        return self.obj_ref()

    @abstractmethod
    def bind(self):
        """ Bind the expression to the `name` attribute on `object`.

        This method will be called after the appropriate items in the
        ui tree have been built such that the namespaces will be 
        fully populated.

        """
        raise NotImplementedError
    
    @abstractmethod
    def eval_expression(self):
        """ Evaluate the expression and return the result. This will be
        called only after `bind` has been called.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Ast walking helpers
#------------------------------------------------------------------------------
def parse_attr_names(py_ast, obj):
    """ Parses an expression ast for attributes on the given obj.

    Given an ast.Expression node and an objet, returns the set of ast 
    Name nodes that are trait attributes on the object. This treats the 
    expression as if 'self' were implicit (ala c++) and we want to find 
    all the traited attributes referred to implicitly in the expression 
    for the purposes of hooking up notifiers.

    Paramters
    ---------
    py_ast : Instance(ast.Expresssion)
        The ast Expression node to parse.
    
    obj : HasTraits object
        The HasTraits instance object we are querrying for attributes.

    Returns
    -------
    result : set
        The set of names referred to in the expression that are trait
        attributes on the object.

    """
    names = set()
    name_node = ast.Name
    for node in ast.walk(py_ast):
        if isinstance(node, name_node):
            name = node.id
            if obj.trait(name) is not None:
                names.add(name)
    return names
    

#------------------------------------------------------------------------------
# Standard Expression Classes
#------------------------------------------------------------------------------
class SimpleExpression(AbstractExpression):
    """ A concrete implementation of AbstractExpression that provides 
    a default attribute value by evaluating the expression.

    See Also
    --------
    AbstractExpression

    """
    __slots__ = ()

    def bind(self):
        """ Bind the expression to the `name` attribute on `object`.

        """
        # Nothing to do for simple expression
        pass

    def eval_expression(self):
        """ Evaluates and returns the results of the expression.

        """
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj})
        val = eval(self.code, f_globals, f_locals)
        return val

    def get_globals(self):
        """ Returns the global namespace dictionary.
        
        Returns the dict created by the `global_ns` callable attribute,
        or raises a TypeError if the value is not a dict.

        """
        global_ns = self.globals_f()
        if type(global_ns) is not dict:
            raise TypeError('The type of the global namespace must be dict')
        return global_ns
    
    def get_locals(self, overrides):
        """ Returns the local namespace mapping.

        Returns the mapping object created by the `local_ns` callable
        attribute, or raises a TypeError if the value is not a mapping.
        A dictionary of overrides can be supplied to inject items into
        the local namespace.

        """
        local_ns = self.locals_f()
        if not isinstance(local_ns, MappingType):
            raise TypeError('The local namespace must be a mapping type')
        return ExpressionLocals(local_ns, self.obj, overrides)


class UpdatingExpression(SimpleExpression):
    """ A dynamically updating concrete expression object. 

    The expression is parsed for trait attribute references and when any
    of those traits in the expression change, the expression is evaluated
    and the value of the component attribute is updated.

    """
    __slots__ = ()

    def bind(self):
        """ Parse the expression for any trait attribute references. A 
        notifier is attached to each trait reference that will update 
        the expression value upon change.

        """
        super(UpdatingExpression, self).bind()

        obj = self.obj
        global_ns = self.get_globals()
        local_ns = self.get_locals({'self': obj})
        py_ast = self.py_ast

        # The attribute visitor parses the expression looking for any 
        # `foo.bar` style attribute sub-expressions. The results value
        # is a list of ('foo', 'bar') style tuples.
        visitor = AttributeVisitor()
        visitor.visit(py_ast)
        
        update_method = self.update_object
        for dep_name, attr in visitor.results():
            try:
                dep = local_ns[dep_name]
            except KeyError:
                try:
                    dep = global_ns[dep_name]
                except KeyError:
                    raise NameError('name `%s` is not defined' % dep_name)
            if isinstance(dep, HasTraits):
                dep.on_trait_change(update_method, attr)
        
        # This portion binds any trait attributes that are being
        # reference via the implicit 'self' feature.
        for name in parse_attr_names(py_ast, obj):
            obj.on_trait_change(update_method, name)

    def update_object(self):
        """ The notification handler to update the component object.

        When this method is called, the expression is re-evaluated, and
        the results are assigned to the proper attribute on the component
        object.

        """
        setattr(self.obj, self.attr_name, self.eval_expression())


class DelegatingExpression(SimpleExpression):
    """ A concrete expression object that performs two-way binding on
    constructs of the from 'foo.bar'

    """
    __slots__ = ('lookup_info',)

    def bind(self):
        """ Parses the expression object for the appropriate 
        lookup names.

        """
        super(DelegatingExpression, self).bind()
        import pdb; pdb.set_trace()
        obj = self.obj
        global_ns = self.get_globals()
        local_ns = self.get_locals({'self': obj})
        
        # The attribute visitor parses the expression looking for any 
        # `foo.bar` style attribute sub-expressions. The results value
        # is a list of ('foo', 'bar') style tuples.
        visitor = AttributeVisitor()
        visitor.visit(self.py_ast)
        deps = visitor.results()

        if len(deps) > 1:
            msg = 'Invalid expression for delegation - lineno (%s)'
            raise TypeError(msg % self.py_ast.lineno)

        dlgt_name, dlgt_attr_name = deps[0]

        try:
            dlgt = local_ns[dlgt_name]
        except KeyError:
            try:
                dlgt = global_ns[dlgt_name]
            except KeyError:
                raise NameError('name `%s` is not defined' % dlgt_name)

        self.lookup_info = (dlgt, dlgt_attr_name)

        if isinstance(dlgt, HasTraits):
            dlgt.on_trait_change(self.update_object, dlgt_attr_name)

        obj.on_trait_change(self.update_delegate, self.attr_name)

    def eval_expression(self):
        """ Overridden from the parent class since we have enough
        information to lookup the delegate more efficiently than 
        a simple eval.

        """
        return getattr(*self.lookup_info)

    def update_object(self):
        """ The notification handler to update the component object.

        When this method is called, the delegate expression is evaluated
        and the results are assigned to the appropriate attribute on 
        the component.

        """
        setattr(self.obj, self.attr_name, self.eval_expression())

    def update_delegate(self, val):
        """ The notification handler to update the delegate object.

        When this method is called, the delegate expression is updated
        with the appropriate value from the component.

        """
        dlgt_obj, dlgt_attr_name = self.lookup_info
        setattr(dlgt_obj, dlgt_attr_name, val)


class NotifyingExpression(SimpleExpression):
    """ A concrete expression object that will eval an expression when 
    the attribute on the object changes. 

    An arguments object will be added to the local namespace of the 
    expression at the 'args' name. This allows the expression to accept
    argument information from the attribute change notification, instead
    of needing to do additional attribute lookups.

    """
    __slots__ = ()

    arguments = namedtuple('Arguments', ('obj', 'name', 'old', 'new'))

    def bind(self):
        """ Overridden from the parent class to hookup a notifier on
        the component attribute.

        """
        super(NotifyingExpression, self).bind()
        self.obj.on_trait_change(self.notify, self.attr_name)

    def eval_expression(self):
        """ Overridden from the parent class to add an arguments object
        to the local namespace.

        """
        obj = self.obj
        name = self.name
        val = getattr(obj, name)
        args = self.arguments(obj, name, None, val)
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj, 'args': args})
        return eval(self.code, f_globals, f_locals)

    def notify(self, obj, name, old, new):
        """ The notification handler that evals the expression in 
        appropriate contexts.

        """
        args = self.arguments(obj, name, old, new)
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj, 'args': args})
        eval(self.code, f_globals, f_locals)

