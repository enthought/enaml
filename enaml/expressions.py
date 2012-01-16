#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import namedtuple, MutableMapping
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
# Expression Locals Notifier
#------------------------------------------------------------------------------
class ExpressionLocalsNotifier(object):
    """ A thin object which manages the lifetime of a subscription to
    an ExpressionLocals mapping.

    """
    __slots__ = ('expr_ref', '__weakref__')

    def __init__(self, expr_locals, key, expr):
        """ Initialize an ExpressionLocalsNotifier.

        Parameters
        ----------
        expr_locals : Instance(ExpressionLocals)
            The ExpressionLocals instance to which we are subscribing.
            No reference is maintained to this object.
        
        key : string
            The key on the locals to subscribe.
        
        expr : Instance(AbstractExpression)
            The expression object which should be notified when the
            value in the locals changes. Only a weak reference is 
            maintained to this object.
        
        """
        self.expr_ref = weakref.ref(expr)
        expr_locals.subscribe(key, self)
    
    def __call__(self, expr_locals, key, old, new):
        expr = self.expr_ref()
        if expr is not None:
            expr.notify(expr_locals, key, old, new)


#------------------------------------------------------------------------------
# Expression Locals
#------------------------------------------------------------------------------
class ExpressionLocals(MutableMapping):
    """ A MutableMapping which adds a 'subcribe' method to register
    callbacks to be called when the value for a particular key as
    been changed. Unlike a normal mapping, instance of this class
    are hashable, and hash like a regular Python class instance.

    """
    def __init__(self, **values):
        """ Initialize an ExpressionLocals instance.

        Paramters
        ---------
        **values
            The default key/value pairs to add to the locals object.
        
        """
        self._data = {}
        self._subscriptions = {}
        self.update(**values)
    
    def __hash__(self):
        """ Makes the mapping hashable so that it can be used a key
        in a dict in order to manage notifiers.

        """
        return object.__hash__(self)

    def __getitem__(self, name):
        """ Returns the value for the name or raises a KeyError.

        """
        return self._data[name]
    
    def __setitem__(self, key, value):
        """ Sets the value for the name, calling subscribers only if
        the value previously existed in the mapping and if the current
        value is different from the old value.

        """
        data = self._data
        if key not in data:
            data[key] = value
        else:
            old = data[key]
            data[key] = value
            if value != old:
                self._call_subscriptions(key, old, value)
    
    def __delitem__(self, key):
        """ Deletes the key from the mapping.

        """
        del self._data[key]

    def __iter__(self):
        """ Returns an iterator for the mapping.

        """
        return iter(self._data)

    def __contains__(self, name):
        """ Returns True if there is a value for the given name, False
        otherwise.

        """
        return name in self._data

    def __len__(self):
        """ Returns the length of the mapping.

        """
        return len(self._data)

    def _call_subscriptions(self, key, old, new):
        """ A private dispatch method which calls any subscribers when
        a value in the mapping has changed.

        """
        subs = self._subscriptions
        if key in subs:
            for cb_ref in subs[key]:
                callback = cb_ref()
                if callback is not None:
                    callback(self, key, old, new)

    def subscribe(self, key, callback):
        """ Subscribe a callback that will be called when the value
        for the key changes in the mapping.

        Parameters
        ----------
        key : string
            The key to track for value changes in the mapping.
        
        callback : callable
            A callable which accets four arguments: this mapping,
            the key, the old value, and the new value. Only a weak
            reference is maintained to this callback.
        
        """
        wr_self = weakref.ref(self)
        def unsub(wr):
            this = wr_self()
            if this is not None:
                subs = self._subscriptions[key]
                try:
                    subs.remove(wr)
                except ValueError:
                    pass
                if not subs:
                    del self._subscriptions[key]
        cb_ref = weakref.ref(callback, unsub)
        self._subscriptions.setdefault(key, []).append(cb_ref)
    

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
    __slots__ = ('obj', 'f_locals', 'f_globals', 'toolkit', 'overrides', 
                 'binder', 'temp_locals')

    def __init__(self, obj, f_locals, f_globals, toolkit, overrides=None, binder=None):
        """ Initialize an expression locals instance.

        Parameters
        ----------
        obj : object
            The python object on which to start looking for attributes.

        f_locals : ExpressionLocals
            The locals object to check before checking the attribute space
            of the given object.

        f_globals : dict
            The globals dict to check after checking the attribute space
            of the given object, but before checking the toolkit.

        toolkit : Toolkit
            The toolkit to check after checking the globals.

        overrides : dict or None
            An optional dictionary of override values to check before
            f_locals.

        binder : callable or None
            An optional callable which is called when an implicit 
            attribute is looked up on the object and should binds any 
            notifiers necessary. The arguments passed are the object
            and the attribute name.

        """
        self.obj = obj
        self.f_locals = f_locals
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
            3) f_locals
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
        # Try temp locals first. The temp locals are assigned via 
        # __setitem__ when a match is not found in f_locals or via
        # implicit attrs. Looking here first is simply a performance
        # hack and is semantically the same if we had placed it 3rd
        # in the lookup order. But since the temp locals is most oft
        # used for the loop variable of list comprehensions, this 
        # performance tweak pays off.
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
        
        # Next, check locals mapping and hookup a notifier on success.
        try:
            res = self.f_locals[name]
        except KeyError:
            pass
        else:
            # Call the binder if given so notifiers can be hooked up.
            binder = self.binder
            if binder is not None:
                binder(self.f_locals, name)
            return res

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
        """ Stores the value according to the following precedence rules:
            1) f_locals
            2) implicit_attrs
            3) temp_locals

        """
        f_locals = self.f_locals
        if name in f_locals:
            f_locals[name] = val
            return
        
        parent = self.obj
        while parent is not None:
            if hasattr(parent, name):
                setattr(parent, name, val)
                return
            else:
                parent = parent.parent

        self.temp_locals[name] = val


#------------------------------------------------------------------------------
# Abstract Expression
#------------------------------------------------------------------------------
class AbstractExpression(object):

    __metaclass__ = ABCMeta

    __slots__ = ('obj_ref', 'attr', 'code', 'f_locals', 'f_globals',
                 'toolkit', '__weakref__')

    def __init__(self, obj, attr, code, f_locals, f_globals, toolkit):
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

        f_locals : ExpressionLocals
            The locals objects that forms the local scope for the
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
        self.f_globals = f_globals
        self.toolkit = toolkit
        self.f_locals = f_locals

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
            self.obj, self.f_locals, self.f_globals, self.toolkit,
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
        elif isinstance(obj, ExpressionLocals):
            # The ExpressionLocals will keep a weakref to the callback
            # but a strong ref will be kept to the notifier in the dict
            # of notifiers on this instance, so we still dont wan't
            # to just subscribe the method. Instead we use a notifier
            # object that manages the lifetime.
            notifier = ExpressionLocalsNotifier(obj, attr, self)
        
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
            self.obj, self.f_locals, self.f_globals, self.toolkit, 
            binder=self.bind_attribute,
        )

        # f_globals is passed as the globals even though the scope
        # object will handle that part of the lookup. The only effect
        # it has here is to make sure that builtins are accesible and
        # avoid the need to create a new "globals" dict each time we
        # do an eval.
        return eval(self.code, self.f_globals, scope)


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
        wr_self = weakref.ref(self)
        def value_getter():
            this = wr_self()
            if this is not None:
                return getattr(this.obj, this.attr)
        
        bp_code = bp.Code.from_code(code)
        attr_code, attr_arg = bp_code.code[-2]
        new_code = bp_code.code[:-2]
        if attr_code == bp.LOAD_ATTR:
            new_code.extend([
                (bp.DUP_TOP, None),
                (bp.LOAD_CONST, value_getter),
                (bp.CALL_FUNCTION, 0x0000),
                (bp.ROT_TWO, None),
                (bp.STORE_ATTR, attr_arg),
                (bp.LOAD_ATTR, attr_arg),
                (bp.RETURN_VALUE, None),
            ])
        elif attr_code == bp.LOAD_NAME and len(new_code) == 1:
            new_code.extend([
                (bp.LOAD_CONST, value_getter),
                (bp.CALL_FUNCTION, 0x0000),
                (bp.STORE_NAME, attr_arg),
                (bp.LOAD_NAME, attr_arg),
                (bp.RETURN_VALUE, None),
            ])
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
            self.obj, self.f_locals, self.f_globals, self.toolkit, 
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
                obj, self.f_locals, self.f_globals, self.toolkit, 
                overrides=overrides,
            )
            eval(self.code, self.f_globals, scope)

