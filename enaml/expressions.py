#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import namedtuple
import weakref

from traits.api import HasTraits, Disallow

from .parsing import byteplay as bp


#------------------------------------------------------------------------------
# Trait Attribute Notifier
#------------------------------------------------------------------------------
class TraitAttributeNotifier(object):
    """ A thin object which manages a trait change notification for
    a SubscriptionExpression affording easy subscription lifetime 
    management.

    """
    __slots__ = ('expr_ref', '__weakref__')

    def __init__(self, obj, attr, expr):
        """ Initialize a TraitAttributeNotifier.

        Parameters
        ----------
        obj : Instance(HasTraits)
            The HasTraits object with the attribute of interest.
        
        attr : string
            The name of the trait attribute on the object which
            should emit a notification on change.
        
        expr : Instance(AbstractExpression)
            The expression object which should be notified when the
            trait attribute on the object changes. Only a weak 
            reference is maintained to this object.
        
        """
        self.expr_ref = weakref.ref(expr)
        obj.on_trait_change(self.notify, attr)

    def notify(self, obj, name, old, new):
        """ The change handler for the subscribed trait attribute.

        """
        expr = self.expr_ref()
        if expr is not None:
            expr.notify(obj, name, old, new)


#------------------------------------------------------------------------------
# Expression Scope
#------------------------------------------------------------------------------
class ExpressionScope(object):
    """ A mapping object that implements the scope resolution order for
    Enaml expressions.

    Notes
    -----
    Strong references are kept to all objects passed to the constructor,
    so care should be taken in managing the lifetime of these scope
    objects since their use is likely to create reference cycles. It is
    probably best to create these scope objects on-the-fly as needed.

    """
    __slots__ = ('obj', 'identifiers', 'f_globals', 'toolkit', 'overrides', 
                 'binder', 'temp_locals')

    def __init__(self, obj, identifiers, f_globals, toolkit, overrides=None, binder=None):
        """ Initialize an expression locals instance.

        Parameters
        ----------
        obj : object
            The python object on which to start looking for attributes.

        identifiers : dict
            The dictionary of identifiers that are available to the
            expression. These are checked before the attribute space
            of the object.

        f_globals : dict
            The globals dict to check after checking the attribute space
            of the given object, but before checking the toolkit.

        toolkit : Toolkit
            The toolkit to check after checking the globals.

        overrides : dict or None
            An optional dictionary of override values to check before
            identifiers.

        binder : callable or None
            An optional callable which is called when an implicit 
            attribute is looked up on the object and should binds any 
            notifiers necessary. The arguments passed are the object
            and the attribute name.

        """
        self.obj = obj
        self.identifiers = identifiers
        self.f_globals = f_globals
        self.toolkit = toolkit
        self.overrides = overrides
        self.binder = binder
        self.temp_locals = {}

    def __getitem__(self, name):
        """ Lookup an item from the namespace.

        Returns the named item from the namespace according to the
        following precedence rules binding notifiers where appropriate:
            1) temp_locals
            2) overrides (if provided)
            3) identifiers
            4) implicit attrs
            5) f_globals
            6) toolkit
            7) builtins
        
        Parameters
        ----------
        name : string
            The name that should be looked up in the namespace.

        Returns
        -------
        result : object
            The value associated with the name, if found.

        """
        # The temp locals are assigned to via __setitem__ when a 
        # STORE_NAME opcode is encountered. The will happen, for
        # example, with the loop variables of a list comprehension.
        # Thus, those must take highest precedence.
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
        
        # Next, check the identifiers.
        try:
            return self.identifiers[name]
        except KeyError:
            pass

        # Next, walk up the ancestor tree starting at self.obj
        # looking for attributes of the given name.
        parent = self.obj
        while parent is not None:
            try:
                res = getattr(parent, name)
            except AttributeError:
                parent = parent.parent
            else:
                # Call the binder if given so notifiers can be hooked up.
                binder = self.binder
                if binder is not None:
                    binder(parent, name)
                return res

        # Next, check the globals dictionary
        try:
            return self.f_globals[name]
        except KeyError:
            pass
        
        # Finally, check the toolkit (will raise KeyError on failure)
        return self.toolkit[name]

    def __setitem__(self, name, val):
        """ Stores the value into the temp locals dict. This operation
        will occur whenever a STORE_NAME opcode is encountered such
        as with the loop variables of a list comprehension, or on
        Python 2.6 to store the list itself. See the docstring of
        __delitem__ for more info.

        """
        self.temp_locals[name] = val

    def __delitem__(self, name):
        """ Deletes the value from the temp locals dict. This operation
        will occur on Python 2.6 during a list comprehension. In that
        version of Python, the list in a list comp is stored in a mangled
        local variable which is not a valid Python name. Presumably, this
        is because the LIST_APPEND opcode on 2.6 consumes the TOS, while
        on 2.7 it does not.

        """
        del self.temp_locals[name]


#------------------------------------------------------------------------------
# Abstract Expression
#------------------------------------------------------------------------------
class AbstractExpression(object):

    __metaclass__ = ABCMeta

    __slots__ = ('obj_ref', 'attr', 'code', 'identifiers', 'f_globals',
                 'toolkit', '__weakref__')

    def __init__(self, obj, attr, code, identifiers, f_globals, toolkit):
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

        identifiers : dict
            The dictionary of identifiers that are available to the
            expression.

        f_globals : dict
            The globals dictionary in which the expression should execute.

        toolkit : Toolkit
            The toolkit that was used to create the object and in which
            the expression should execute.

        """
        # We keep a weakref to obj to avoid ref cycles
        self.obj_ref = weakref.ref(obj)
        self.attr = attr
        self.code = code
        self.identifiers = identifiers
        self.f_globals = f_globals
        self.toolkit = toolkit

    @property
    def obj(self):
        return self.obj_ref()

    @abstractmethod
    def eval(self):
        """ Evaluate the expression and return the result.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Standard Expression Classes
#------------------------------------------------------------------------------
class SimpleExpression(AbstractExpression):
    """ A concrete implementation of AbstractExpression that provides
    a default attribute value by evaluating the expression.

    """
    __slots__ = ()

    def eval(self):
        """ Evaluates and returns the results of the expression.

        """
        scope = ExpressionScope(
            self.obj, self.identifiers, self.f_globals, self.toolkit,
        )
        # f_globals is passed as the globals even though the scope
        # object will handle that part of the lookup. The only effect
        # it has here is to make sure that builtins are accesible and
        # avoid the need to create a new "gobals" dict each time we
        # do an eval.
        return eval(self.code, self.f_globals, scope)


class SubscriptionExpression(AbstractExpression):
    """ A dynamically updating concrete expression object. This 
    expression will hookup the necessary notifiers during execution
    so that the expression can be reevaluation when any of its 
    subcriptions are fired.

    """
    __slots__ = ('notifiers',)

    def __init__(self, *args):
        super(SubscriptionExpression, self).__init__(*args)
        self.code = self.inject_binding_code(self.code)
        self.notifiers = weakref.WeakKeyDictionary()

    def inject_binding_code(self, code):
        """ Injects code into the code object which will call a binder 
        callback when attributes are accessed.

        """
        # Create a closure which holds a weak reference to this expression
        # so that it is suitable to pass into code object without leaking
        # memory or creating undue reference cycles. The closure will 
        # bind a listener to a trait attribute on a given object.
        wr_self = weakref.ref(self)
        def code_binder(obj, attr):
            this = wr_self()
            if this is not None:
                this.bind_attribute(obj, attr)

        new_code = []
        bp_code = bp.Code.from_code(code)
        for op, op_arg in bp_code.code:
            if op == bp.LOAD_ATTR:
                new_code.extend([
                    (bp.DUP_TOP, None),
                    (bp.LOAD_CONST, code_binder),
                    (bp.ROT_TWO, None),
                    (bp.LOAD_CONST, op_arg),
                    (bp.CALL_FUNCTION, 0x0002),
                    (bp.POP_TOP, None),
                ])
            new_code.append((op, op_arg))
        bp_code.code = new_code
        return bp_code.to_code()

    def notify(self, obj, name, old, new):
        """ The callback to be use by notifiers when the component should
        be updated with the new value of the expression.

        """
        self.update_component()
    
    def update_component(self):
        """ Updates the value of the component attribute with the new
        value of the expression.

        """
        setattr(self.obj, self.attr, self.eval())

    def bind_attribute(self, obj, attr):
        """ Hooks up the necessary notifier for the given object and
        attribute which, when fired, will update the value of the 
        attribute on the component.

        """
        # Only hook up a notifier if one does not already exist.
        notifiers = self.notifiers
        if obj in notifiers:
            if attr in notifiers[obj]:
                return

        notifier = None
        if isinstance(obj, HasTraits):
            # Only hook up a notifier if the attribute access refers
            # to a proper trait. We check for Disallow trait types 
            # since those can be returned by instances of HasStrictTraits
            trait = obj.trait(attr)
            if trait is not None and trait.trait_type is not Disallow:
                # A notifier object is used here instead of binding to a 
                # method on this Expression instance since the lifetime 
                # of the trait change notification is tied to the that
                # of the notifier object. Hence, using such an object
                # eliminates the need for us to explicitly unsubscribe
                # any old handlers each time we evaluate the expression.
                # We simply just delete the old notifiers.
                notifier = TraitAttributeNotifier(obj, attr, self)
        
        if notifier is not None:
            if obj in notifiers:
                notifiers[obj][attr] = notifier
            else:
                notifiers[obj] = {attr: notifier}

    def eval(self):
        # Notifiers are hooked up every time the expression is evaluated
        # this is required if we want to avoid maintaining a ton of state.
        # Consider an expression such as [a.b for a in foo()]. We need
        # to update the value of this expression whenever the 'b' attr
        # of an item in bar.foo changes or when bar.foo changes. Let's 
        # assume bar.foo changes, there is no guarantee that the items
        # of the old bar.foo have been destroyted, so in order to unhook
        # the old notifiers, we would need to keep the state of what has
        # been previously bound. Rather than consume that memory, we bind
        # and destroy the notifiers on every cycle of the expression. We 
        # clear the notifiers before evaluation so that we don't get 
        # duplicate notifications.
        self.notifiers.clear()

        scope = ExpressionScope(
            self.obj, self.identifiers, self.f_globals, self.toolkit, 
            binder=self.bind_attribute,
        )

        # f_globals is passed as the globals even though the scope
        # object will handle that part of the lookup. The only effect
        # it has here is to make sure that builtins are accesible and
        # avoid the need to create a new "globals" dict each time we
        # do an eval.
        return eval(self.code, self.f_globals, scope)


def _set_implicit_attr(obj, name, val):
    """ A private delegating expression helper which walks up the object 
    tree and attempts to perform the setattr operation on an attribute. 
    If the attribute is not found in the tree, a NameError is raised.

    Parameters
    ----------
    obj : BaseComponent
        The BaseComponent instance at which we should begin looking
        for a valid attribute to set.
    
    name : string
        The name of the attribute we are wanting to set.
    
    val : object
        The value to set on the attribute.

    """
    while obj is not None:
        if hasattr(obj, name):
            setattr(obj, name, val)
            return
        else:
            obj = obj.parent
    raise NameError("name '%s' is not defined" % name)


class DelegatingExpression(SubscriptionExpression):
    """ A SubscriptionExpression subclass that performs two-way binding
    and restricts the expression to the form "<expr>.attr".

    """
    __slots__ = ('setter_code',)

    def __init__(self, *args):
        super(DelegatingExpression, self).__init__(*args)
        self.setter_code = self.make_setter_code(self.code)
        self.obj.on_trait_change(self.update_expression, self.attr)

    def make_setter_code(self, code):
        """ Create the bytecode expression which performs the setattr
        part of the delegation. This is implemented by copying the
        bytecode of the getattr expression, and modifying its tail
        to convert it into a setting operation.

        """
        # The last opcode is always RETURN_VALUE. The one before that
        # will determine whether we have a delegatable expression.
        bp_code = bp.Code.from_code(code)
        attr_code, attr_arg = bp_code.code[-2]
        new_code = bp_code.code[:-2]

        # In both of the below cases, we end with a LOAD_ATTR and 
        # RETURN_VALUE so that the calling code can determine if
        # the setting operation caused a change in the value, if
        # it did, it will attempt to cycle again to find stability.

        # If the tail of the expression is a getattr, we replace it
        # with a setattr(tail(), tail_attr, getattr(self, self_attr))
        if attr_code == bp.LOAD_ATTR:
            new_code.extend([
                (bp.DUP_TOP, None),
                (bp.LOAD_NAME, 'self'),
                (bp.LOAD_ATTR, self.attr),
                (bp.ROT_TWO, None),
                (bp.STORE_ATTR, attr_arg),
                (bp.LOAD_ATTR, attr_arg),
                (bp.RETURN_VALUE, None),
            ])
        
        # If the expression is simply a name, then we assume its an 
        # implicit attribute lookup since, delegating to an identifier
        # would be irresponsible (we check for this). We convert the 
        # load name into an implicit attribute setter using a helper 
        # function which walks up the tree.
        elif attr_code == bp.LOAD_NAME and len(new_code) == 1:
            if attr_arg in self.identifiers:
                msg = "Cannot delegate to identifier '%s'"
                raise ValueError(msg % attr_arg)
            new_code.extend([
                (bp.LOAD_CONST, _set_implicit_attr),
                (bp.LOAD_NAME, 'self'),
                (bp.DUP_TOP, None),
                (bp.LOAD_CONST, attr_arg),
                (bp.ROT_TWO, None),
                (bp.LOAD_ATTR, self.attr),
                (bp.CALL_FUNCTION, 0x0003),
                (bp.POP_TOP, None),
                (bp.LOAD_NAME, attr_arg),
                (bp.RETURN_VALUE, None),
            ])

        # Otherise, we are unable to delegate to the expression
        # and we raise an error to that effect.
        else:
            # XXX need error message that reports enaml line numbers
            raise TypeError('Invalid Expression for Delegation')

        bp_code.code = new_code
        
        return bp_code.to_code()

    def update_component(self):
        """ The notification handler to update the component object.

        When this method is called, the delegate expression is evaluated
        and the results are assigned to the appropriate attribute on
        the component.

        """
        obj = self.obj
        attr = self.attr
        val = self.eval()
        setattr(obj, attr, val)
        new_val = getattr(obj, attr)
        if val != new_val:
            self.update_expression()

    def update_expression(self):
        """ The notification handler to update the delegate object.

        When this method is called, the delegate expression is updated
        with the appropriate value from the component.

        We guard against circular notifications, but try to ensure that we
        end up in a consistent state, ie. when all is said and done, the
        object and the delegate end up with the same value.

        """
        val = getattr(self.obj, self.attr)
        new_val = self.eval_setter()
        if val != new_val:
            self.update_component()

    def eval_setter(self):
        scope = ExpressionScope(
            self.obj, self.identifiers, self.f_globals, self.toolkit, 
        )
        return eval(self.setter_code, self.f_globals, scope)


class NotifyingExpression(AbstractExpression):
    """ A concrete expression object that will evaluate an expression 
    when the attribute on the object changes.

    """
    __slots__ = ()

    #: A namedtuple which is used to pass arguments to the expression.
    arguments = namedtuple('arguments', 'obj name old new')

    #: A WeakKeyDictionary which is used to hold the instances of the
    #: NotifyingExpression. The keys of the dict are the components
    #: to which the expressions are listening and the values are lists
    #: of instances. Thus, there is no need to store these instances
    #: on a component. The instances are added as they are created.
    instances = weakref.WeakKeyDictionary()

    def __init__(self, *args):
        super(NotifyingExpression, self).__init__(*args)
        trait = self.obj.trait(self.attr)
        if trait is None or trait is Disallow:
            msg = "Cannot bind expression. %s object has no attribute '%s'"
            raise AttributeError(msg % (self.obj, self.attr))
        self.obj.on_trait_change(self.handle_cmpnt_changed, self.attr)
        NotifyingExpression.instances.setdefault(self.obj, []).append(self)

    def eval(self):
        """ Evaluates the expression and return the results. A notifying
        expression does not return results so this method simply returns
        None. The expression is properly evaluated whenever the object
        attribute changes.

        """
        return None

    def handle_cmpnt_changed(self, obj, name, old, new):
        """ Evaluates the expression while adding an 'args' object to the
        expression scope.

        """
        if obj.initialized:
            args = self.arguments(obj, name, old, new)
            overrides = {'args': args}
            scope = ExpressionScope(
                obj, self.identifiers, self.f_globals, self.toolkit, 
                overrides=overrides,
            )
            eval(self.code, self.f_globals, scope)

