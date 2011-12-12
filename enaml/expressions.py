#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import ast
from abc import ABCMeta, abstractmethod
from collections import namedtuple
import weakref

from traits.api import HasTraits

from .parsing.analyzer import AttributeVisitor
from .guard import guard


# XXX clean up the expression binders. We need more powerful visitors which
# perform more intelligent binding.

#------------------------------------------------------------------------------
# Express Locals
#------------------------------------------------------------------------------
class ExpressionLocals(object):
    """ A mapping object that will first look in the provided locals
    dictionary and finally by walking up the tree of components looking
    for attributes.

    Notes
    -----
    When setting items on this mapping, the values are stored in an 
    internal dictionary. Modifying the f_locals is not desired since
    that would effect all other expressions that operate with those
    locals. However, we must support assignment since that's required
    to make list comprehensions work.

    Strong references are kept to all objects passed to the constructor,
    so care should be taken in managing the lifetime of these scope
    objects since their use is likely to create reference cycles.
    (It's probably best to create these objects on-the-fly when needed)

    """
    __slots__ = ('obj', 'f_locals', 'overrides', 'temp_locals')

    def __init__(self, obj, f_locals, overrides=None):
        """ Initialize an expression locals instance.

        Parameters
        ----------
        obj : object
            The python object on which to start looking for attributes.

        f_locals : dict
            The locals dict to check before checking the attribute space
            of the given object.

        overrides : dict or None
            A dictionary of override values to check before locals.

        """
        self.obj = obj
        self.f_locals = f_locals
        self.overrides = overrides
        self.temp_locals = {}

    def __getitem__(self, name):
        """ Lookup an item from the namespace.

        Returns the named item from the namespace by first looking in
        the provided locals namespace, and finally the attribute space 
        of the object. If the value is not found, a KeyError is raised.

        Parameters
        ----------
        name : string
            The name that should be looked up in the namespace.

        Returns
        -------
        result : object
            The value associated with the name, if found.

        """
        # Try temp locals first so that list comps work properly
        try:
            return self.temp_locals[name]
        except KeyError:
            pass

        # Next, check the overrides if given
        overrides = self.overrides
        if overrides is not None:
            try:
                return overrides[name]
            except KeyError:
                pass
        
        # Next, check locals dict
        try:
            return self.f_locals[name]
        except KeyError:
            pass

        # Finally, walk up the ancestor tree starting at self.obj
        # looking for attributes of the given name.
        parent = self.obj
        while True:
            try:
                return getattr(parent, name)
            except AttributeError:
                parent = parent.parent
                if parent is None:
                    raise KeyError(name)

    def __setitem__(self, name, val):
        """ Stores the value in the internal locals dictionary. This
        allows list comprehension expressions to work properly.

        """
        self.temp_locals[name] = val


#------------------------------------------------------------------------------
# Ast walking helpers
#------------------------------------------------------------------------------
def parse_attr_names(py_ast, obj, f_locals):
    """ Parses an expression ast, looking for attributes references in
    the objects attribute space.

    Given an ast.Expression node and an objet, returns the set of tuples
    which are (name, object) parents. The name is an attribute name an
    the object is the object which contains the trait attribute and is
    either 'obj' itself or some ancestor of obj.

    Parameters
    ----------
    py_ast : Instance(ast.Expresssion)
        The ast Expression node to parse.

    obj : HasTraits object
        The HasTraits instance object we are querrying for attributes.

    f_locals : dict
        The local dictionary whose names override those of the attribute
        space.

    Returns
    -------
    result : set
        The set of (name, object) pairs referred to in the expression that 
        are trait attributes on some ancestor of obj.

    """
    pairs = set()
    name_node = ast.Name
    for node in ast.walk(py_ast):
        if isinstance(node, name_node):
            name = node.id
            if name not in f_locals:
                parent = obj
                while parent is not None:
                    # XXX I don't particularly like this way of testing
                    # whether or not an object has a trait defined.
                    # Calling obj.trait(name) doesn't work because the
                    # parent class is HasStrictTraits, so we get a trait
                    # returned which is the Disallow trait type.
                    if (name in parent._instance_traits() or 
                        name in parent.class_traits()):
                        pairs.add((name, parent))
                        break
                    parent = parent.parent
    return pairs


#------------------------------------------------------------------------------
# Abstract Expression
#------------------------------------------------------------------------------
class AbstractExpression(object):

    __metaclass__ = ABCMeta

    __slots__ = ('obj_ref', 'attr', 'expr_ast', 'code', 'f_globals',
                 'toolkit', 'f_locals', '__weakref__')

    def __init__(self, obj, attr, expr_ast, code, f_globals, toolkit, f_locals):
        """ Initializes and expression object.

        Parameters
        ----------
        obj : HasTraits instance
            The HasTraits instance to which we are binding the expression.

        attr : string
            The attribute name on `obj` to which this expression is bound.

        expr_ast : ast.Expression instance
            An ast.Expression node instance which is the rhs expression.

        code : types.CodeType object
            The compiled code object for the provided ast node.

        f_globals : dict
            The globals dictionary in which the expression should execute.

        toolkit : Toolkit
            The toolkit that was used to create the object and in which
            the expression should execute.
        
        f_locals : dict
            The dictionary of objects that form the local scope for the
            expression.

        """
        # We keep a weakref to obj to avoid ref cycles
        self.obj_ref = weakref.ref(obj)
        self.attr = attr
        self.expr_ast = expr_ast
        self.code = code
        self.f_globals = f_globals
        self.toolkit = toolkit
        self.f_locals = f_locals

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
        f_locals = self.get_locals()
        val = eval(self.code, f_globals, f_locals)
        return val

    def get_globals(self):
        """ Returns the global namespace dictionary which is the union
        of f_globals and the toolkit, f_globals taking precedence.

        """
        d = {}
        d.update(self.toolkit)
        d.update(self.f_globals)
        return d

    def get_locals(self):
        """ Returns the local namespace mapping object. The mapping
        object first attempts to lookup the value in f_locals, then
        continues by walking up the tree checking the attributes of
        all the parents.

        """
        return ExpressionLocals(self.obj, self.f_locals)


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
        local_ns = self.get_locals()
        expr_ast = self.expr_ast

        # The attribute visitor parses the expression looking for any
        # `foo.bar` style attribute sub-expressions. The results value
        # is a list of ('foo', 'bar') style tuples.
        visitor = AttributeVisitor()
        visitor.visit(expr_ast)

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
        # referenced via implicit attribute access.
        for name, owner in parse_attr_names(expr_ast, obj, self.f_locals):
            owner.on_trait_change(update_method, name)

    def update_object(self):
        """ The notification handler to update the component object.

        When this method is called, the expression is re-evaluated, and
        the results are assigned to the proper attribute on the component
        object.

        """
        setattr(self.obj, self.attr, self.eval_expression())


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
        obj = self.obj
        global_ns = self.get_globals()
        local_ns = self.get_locals()

        # There are two options for a delegating expression, those
        # of the form 'foo.bar' and those of the form 'foo'.
        if isinstance(self.expr_ast.body, ast.Name):
            pairs = parse_attr_names(self.expr_ast, obj, self.f_locals)
            if len(pairs) != 1:
                msg = 'Delegation expression does not resolve - lineno (%s)'
                raise TypeError(msg % self.expr_ast.lineno)
            dlgt_attr_name, dlgt = pairs.pop()
        else:
            # The attribute visitor parses the expression looking for any
            # `foo.bar` style attribute sub-expressions. The results value
            # is a list of ('foo', 'bar') style tuples.
            visitor = AttributeVisitor()
            visitor.visit(self.expr_ast)
            deps = visitor.results()
            if len(deps) > 1:
                msg = 'Invalid expression for delegation - lineno (%s)'
                raise TypeError(msg % self.expr_ast.lineno)
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

        obj.on_trait_change(self.update_delegate, self.attr)

    def update_object(self, val):
        """ The notification handler to update the component object.

        When this method is called, the delegate expression is evaluated
        and the results are assigned to the appropriate attribute on
        the component.

        We guard against circular notifications, but try to ensure that we
        end up in a consistent state, ie. when all is said and done, the
        object and the delegate end up with the same value.

        """
        dlgt_obj, dlgt_attr_name = self.lookup_info
        # guard against re-setting the object on a change
        with guard(self.obj, self.attr):
            # We add "self" to the guard signature since multiple expressions
            # may delegate to the same dlgt_obj, dlgt_attr_name pair. If
            # we didn't include "self", then only one of these multiple 
            # expressions would be updated since the first one to grab the
            # guard would lock out all the others.
            if not guard.guarded(self, dlgt_obj, dlgt_attr_name):
                setattr(self.obj, self.attr, val)
                new_val = getattr(self.obj, self.attr)
                if new_val != val:
                    # we ended up with a different value on the object than we have
                    # on the delegate.  We need to push this back to the delegate,
                    # and we want to guard against further changes
                    with guard(self, dlgt_obj, dlgt_attr_name):
                        setattr(dlgt_obj, dlgt_attr_name, new_val)

    def update_delegate(self, val):
        """ The notification handler to update the delegate object.

        When this method is called, the delegate expression is updated
        with the appropriate value from the component.

        We guard against circular notifications, but try to ensure that we
        end up in a consistent state, ie. when all is said and done, the
        object and the delegate end up with the same value.

        """
        dlgt_obj, dlgt_attr_name = self.lookup_info
        # guard against re-setting the delegate on a change
        # We add "self" to the guard signature since multiple expressions
        # may delegate to the same dlgt_obj, dlgt_attr_name pair. If
        # we didn't include "self", then only one of these multiple 
        # expressions would be updated since the first one to grab the
        # guard would lock out all the others.
        with guard(self, dlgt_obj, dlgt_attr_name):
            if not guard.guarded(self.obj, self.attr):
                setattr(dlgt_obj, dlgt_attr_name, val)
                new_val = getattr(dlgt_obj, dlgt_attr_name)
                if new_val != val:
                    # we ended up with a different value on the delegate than we have
                    # on the object.  We need to push this back to the object,
                    # and we want to guard against further changes
                    with guard(self.obj, self.attr):
                        setattr(self.obj, self.attr, new_val)


class NotifyingExpression(SimpleExpression):
    """ A concrete expression object that will eval an expression when
    the attribute on the object changes.

    """
    __slots__ = ()

    arguments = namedtuple('arguments', 'obj name old new')

    def bind(self):
        """ Overridden from the parent class to hookup a notifier on
        the component attribute.

        """
        super(NotifyingExpression, self).bind()
        self.obj.on_trait_change(self.eval_expression, self.attr)

    def eval_expression(self, obj, name, old, new):
        """ Overridden from the parent class to add the arguments object
        to the expression locals.

        """
        args = self.arguments(obj, name, old, new)
        f_globals = self.get_globals()
        f_locals = self.get_locals()
        f_locals.overrides = {'args': args}
        val = eval(self.code, f_globals, f_locals)
        return val

