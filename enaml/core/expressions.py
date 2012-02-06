#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import namedtuple, defaultdict
from contextlib import contextmanager
from weakref import ref

from traits.api import Disallow

from .byteplay import Code
from .monitors import AbstractMonitor
from .signaling import Signal


#------------------------------------------------------------------------------
# Expression Helpers
#------------------------------------------------------------------------------
@contextmanager
def swap_attribute(obj, attr, value):
    """ Swap an attribute of an object with the given value for the 
    duration of the context, restoring it on exit. The attribute must
    already exist on the object prior to entering the context.

    Parameters
    ----------
    obj : object
        The object which owns the attribute.
    
    attr : string
        The name of the attribute on the object.

    value : object
        The value to apply to the attribute for the duration of the
        context.
    
    """
    old = getattr(obj, attr)
    setattr(obj, attr, value)
    yield
    setattr(obj, attr, old)


#------------------------------------------------------------------------------
# Execution Scope
#------------------------------------------------------------------------------
class ExecutionScope(object):
    """ A custom mapping object that implements the scope resolution 
    order for the evaluation of code objects in Enaml expressions.

    Notes
    -----
    Strong references are kept to all objects passed to the constructor,
    so these scope objects should be created as needed and discarded in
    order to avoid issues with reference cycles.

    """
    def __init__(self, obj, identifiers, f_globals, toolkit, overrides, cb):
        """ Initialize an execution scope.

        Parameters
        ----------
        obj : BaseComponent
            The BaseComponent instance on which the expression is bound.

        identifiers : dict
            The dictionary of identifiers that are available to the
            expression. These are checked before the attribute space
            of the component.

        f_globals : dict
            The globals dict to check after checking the attribute space
            of the given component, but before checking the toolkit.

        toolkit : Toolkit
            The toolkit to check after checking the globals.

        overrides : dict
            An dictionary of override values to check before identifiers.

        cb : callable or None
            A callable which is called when an implicit attribute is 
            found and accessed on the object. The arguments passed are 
            the object and the attribute name.

        """
        self._obj = obj
        self._identifiers = identifiers
        self._f_globals = f_globals
        self._toolkit = toolkit
        self._overrides = overrides
        self._attr_cb = cb
        self._assignments = {}

    def __getitem__(self, name):
        """ Lookup an item from the namespace.

        Returns the named item from the namespace according to the
        following precedence rules:

            1) assignments
            2) override
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

        Raises
        ------
        KeyError
            If the name is not found, a KeyError is raise.

        """
        # Check the assignments dict first since this is where all
        # local variable assignments will be stored.
        dct = self._assignments
        if name in dct:
            return dct[name]

        # The overrides have the highest precedence of all framework
        # supplied values.
        dct = self._overrides
        if name in dct:
            return dct[name]
        
        # Identifiers have the highest precedence of value able to
        # be supplied by a user of the framework.
        dct = self._identifiers
        if name in dct:
            return dct[name]

        # After identifiers, the implicit attributes of the component
        # hierarchy have precedence.
        parent = self._obj
        while parent is not None:
            try:
                res = getattr(parent, name)
            except AttributeError:
                parent = parent.parent
            else:
                # Call the attribute callback if given.
                cb = self._attr_cb
                if cb is not None:
                    cb(parent, name)
                return res

        # Global variables come after implicit attributes
        dct = self._f_globals
        if name in dct:
            return dct[name]
        
        # End with the toolkit which will raise KeyError on failure.
        # Builtins will be checked by Python using the global dict.
        return self._toolkit[name]

    def __setitem__(self, name, val):
        """ Stores the value into the internal assignments dict. This 

        """
        self._assignments[name] = val

    def __delitem__(self, name):
        """ Deletes the value from the internal assignments dict.

        """
        del self._assignments[name]

    def __contains__(self, name):
        """ Return True if the name is found in the scope, False 
        otherwise.

        """
        # This method must be supplied in order for pdb to work properly
        # from within code blocks. Any attribute callback is temporarily
        # uninstalled so that it is not executed when simply checking for
        # the existance of the item in the scope.
        with swap_attribute(self, '_attr_cb', None):
            if isinstance(name, basestring):
                try:
                    self.__getitem__(name)
                except KeyError:
                    res = False
                else:
                    res = True
            else:
                res = False
        return res


#------------------------------------------------------------------------------
# Nonlocal Scope
#------------------------------------------------------------------------------
class NonlocalScope(object):
    """ An object which implements implicit attribute scoping starting
    at a given object in the tree. It is used in conjuction with a 
    nonlocals() instance to allow for explicit referencing of values
    which would otherwise be implicitly scoped.

    """
    def __init__(self, obj, cb):
        """ Initialize a nonlocal scope.

        Parameters
        ----------
        obj : BaseComponent
            The BaseComponent instance which forms the first level of
            the scope.
        
        cb : callable or None
            A callable which is called when an implicit attribute is 
            found and accessed on the object. The arguments passed are 
            the object and the attribute name.
        
        """
        self._nls_obj = obj
        self._nls_attr_cb = cb

    def __repr__(self):
        """ A pretty representation of the NonlocalScope.

        """
        templ = 'NonlocalScope[%s]'
        return templ % self._nls_obj

    def __call__(self, level=0):
        """ Returns a new nonlocal scope object offset the given number
        of levels in the hierarchy.

        Parameters
        ----------
        level : int, optional
            The number of levels up the tree to offset. The default is
            zero and indicates no offset. The level must be >= 0.

        """
        if not isinstance(level, int) or level < 0:
            msg = ('The nonlocal scope level must be an int >= 0. '
                   'Got %r instead.')
            raise ValueError(msg % level)

        offset = 0
        target = self._nls_obj
        while target is not None and offset != level:
            target = target.parent
            offset += 1

        if offset != level:
            msg = 'Scope level %s is out of range'
            raise ValueError(msg % level)

        return NonlocalScope(target, self._nls_attr_cb)

    def __getattr__(self, name):
        """ A convenience method which allows accessing items in the
        scope via getattr instead of getitem.

        """
        try:
            return self.__getitem__(name)
        except KeyError:
            msg = "%s has no attribute '%s'" % (self, name)
            raise AttributeError(msg)

    def __setattr__(self, name, value):
        """ A convenience method which allows setting items in the 
        scope via setattr instead of setitem.

        """
        if name in ('_nls_obj', '_nls_attr_cb'):
            super(NonlocalScope, self).__setattr__(name, value)
        else:
            try:
                self.__setitem__(name, value)
            except KeyError:
                msg = "%s has no attribute '%s'" % (self, name)
                raise AttributeError(msg)

    def __getitem__(self, name):
        """ Returns the named item beginning at the current scope object
        and progressing up the tree until the named attribute is found.
        A KeyError is raised if the attribute is not found.

        """
        parent = self._nls_obj
        while parent is not None:
            try:
                res = getattr(parent, name)
            except AttributeError:
                parent = parent.parent
            else:
                cb = self._nls_attr_cb
                if cb is not None:
                    cb(parent, name)
                return res
        raise KeyError(name)
    
    def __setitem__(self, name, value):
        """ Sets the value of the scope by beginning at the current scope
        object and progressing up the tree until the named attribute is 
        found. A KeyError is raise in the attribute is not found.

        """
        parent = self._nls_obj
        while parent is not None:
            if hasattr(parent, name):
                setattr(parent, name, value)
                return
            else:
                parent = parent.parent
        raise KeyError(name)

    def __contains__(self, name):
        """ Return True if the name is found in the scope, False 
        otherwise.

        """
        with swap_attribute(self, '_nls_attr_cb', None):
            if isinstance(name, basestring):
                try:
                    self.__getitem__(name)
                except KeyError:
                    res = False
                else:
                    res = True
            else:
                res = False
        return res


#------------------------------------------------------------------------------
# Abstract Expression
#------------------------------------------------------------------------------
class AbstractExpression(object):
    """ The base abstract expression class which defines the base api
    for Expression handlers. These objects are typically created by
    the Enaml operators.

    """
    __metaclass__ = ABCMeta

    #: A signal which is emitted when the expression has changed. It is
    #: emmitted with three arguments: expression, name, and value; where 
    #: expression is the instance which emitted the signal, name is the 
    #: attribute name to which the expression is bound, and value is the
    #: computed value of the expression.
    expression_changed = Signal()

    def __init__(self, obj, name, code, identifiers, f_globals, toolkit):
        """ Initializes and expression object.

        Parameters
        ----------
        obj : BaseComponent
            The base component to which this expression is being bound.

        name : string
            The name of the attribute on the owner to which this 
            expression is bound.

        code : types.CodeType object
            The compiled code object for the Python expression.

        identifiers : dict
            The dictionary of identifiers that are available to the
            expression.

        f_globals : dict
            The globals dictionary in which the expression should execute.

        toolkit : Toolkit
            The toolkit that was used to create the object and in which
            the expression should execute.

        """
        self.obj_ref = ref(obj)
        self.name = name
        self.code = code
        self.identifiers = identifiers
        self.f_globals = f_globals
        self.toolkit = toolkit

    @abstractmethod
    def eval(self):
        """ Evaluates the expression and returns the result. If an 
        expression does not provide (or cannot provide) a value, it 
        should return NotImplemented.
        
        Returns
        -------
        result : object or NotImplemented
            The result of evaluating the expression or NotImplemented
            if the expression is unable to provide a value.
        
        """
        raise NotImplementedError

    @abstractmethod
    def notify(self, old, new):
        """ A method called by the owner component when the trait on 
        which it is bound has changed.

        Parameters
        ----------
        old : object
            The old value of the attribute.
        
        new : object
            The new value of the attribute.
    
        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Simple Expression
#------------------------------------------------------------------------------
class SimpleExpression(AbstractExpression):
    """ A concrete implementation of AbstractEvalExpression. An instance
    of SimpleExpression does not track changes in the expression or emit
    the expression_changed signal. Is also does not support notification.

    """
    def eval(self):
        """ Evaluates and returns the results of the expression.

        """
        obj = self.obj_ref()
        if obj is None:
            return NotImplemented
        
        overrides = {'nonlocals': NonlocalScope(obj, None)}
        identifiers = self.identifiers
        f_globals = self.f_globals
        toolkit = self.toolkit
        scope = ExecutionScope(
            obj, identifiers, f_globals, toolkit, overrides, None,
        )

        with toolkit:
            res =  eval(self.code, f_globals, scope)
        
        return res

    def notify(self, old, new):
        """ A no-op notification method since SimpleExpression does not
        support notification.

        """
        pass


#------------------------------------------------------------------------------
# Notifification Expression
#------------------------------------------------------------------------------
class NotificationExpression(AbstractExpression):
    """ A concrete implementation of AbstractExpression. An instance 
    of NotificationExpression does not support evaluation and does not
    emit the expression_changed signal, but it does support notification. 
    An 'event' object will be added to the scope of the expression which
    will contain information about the trait change.

    """
    #: A namedtuple which is used to pass arguments to the expression.
    event = namedtuple('event', 'obj name old new')

    def eval(self):
        """ A no-op eval method since NotificationExpression does not
        support evaluation.

        """
        return NotImplemented

    def notify(self, old, new):
        """ Evaluates the underlying expression, and provides an 'event'
        object in the evaluation scope which contains information about 
        the trait change.

        """
        obj = self.obj_ref()
        if obj is None:
            return

        identifiers = self.identifiers
        f_globals = self.f_globals
        toolkit = self.toolkit
        override = {
            'event': self.event(obj, self.name, old, new),
            'nonlocals': NonlocalScope(obj, None),
        }
        scope = ExecutionScope(
            obj, identifiers, f_globals, toolkit, override, None,
        )

        with toolkit:
            eval(self.code, f_globals, scope)


#------------------------------------------------------------------------------
# Update Expression
#------------------------------------------------------------------------------
class UpdateExpression(AbstractExpression):
    """ A concrete implementation of AbstractExpression which sets the 
    value on the contituents of the expression according to any provided
    inverters.

    """
    def __init__(self, inverter_classes, *args):
        """ Initialize an UpdateExpression

        Parameters
        ----------
        inverter_classes : iterable of AbstractInverter subclasses
            An iterable of concrete AbstractInverter subclasses which
            will invert the given expression code into a mirrored 
            operation which sets the value on the appropriate object.
        
        *args
            The arguments required to initialize an AbstractExpression
        
        """
        super(UpdateExpression, self).__init__(*args)
        
        inverters = []
        bp_code = Code.from_code(self.code)
        code_list = bp_code.code

        for inv_cls in inverter_classes:
            inverter = inv_cls()
            new_code = inverter.get_inverted_code(code_list)
            if new_code is not None:
                bp_code.code = new_code
                inverters.append(bp_code.to_code())
        
        if not inverters:
            msg = ("Unable to delegate expression to the '%s' attribute of "
                   "the %s object. The provided expression is not structured "
                   "in a way which is suitable for delegation by any of "
                   "the supplied code inverters.")
            raise ValueError(msg % (self.name, self.obj_ref()))

        self.inverters = tuple(inverters)
    
    def eval(self):
        """ A no-op eval method since UpdateExpression does not support 
        evaluation.

        """
        return NotImplemented

    def notify(self, old, new):
        """ A notification method which runs through the list of inverted
        code objects which attempt to set the value. The process stops on
        the first successful inversion. If none of the invertors are 
        successful, a RuntimeError is raised.

        """
        obj = self.obj_ref()
        if obj is None:
            return

        # The override dict is populated with information about the
        # expression and the change. The values allow the generated
        # inverter codes to access the information which is required
        # to perform the operation. The items are added using names
        # which are not valid Python identifiers and therefore do
        # not risk clashing with names in the expression. This is
        # the same technique used by the Python interpreter itself.
        identifiers = self.identifiers
        f_globals = self.f_globals
        toolkit = self.toolkit
        overrides = {
            '_[expr]': self, '_[obj]': obj, '_[old]': old, '_[new]': new, 
            '_[name]': self.name, 'nonlocals': NonlocalScope(obj, None),
        }
        scope = ExecutionScope(
            obj, identifiers, f_globals, toolkit, overrides, None,
        )

        # Run through the inverters, giving each a chance to do the
        # inversion. The process ends with the first success. If 
        # none of the invertors are successful an error is raised.
        with toolkit:
            for inverter in self.inverters:
                if eval(inverter, f_globals, scope):
                    break
            else:
                msg = ("Unable to delegate expression to the '%s' attribute "
                       "of the %s object. None of the provided inverters were "
                       "successful in assigning the value.")
                raise RuntimeError(msg)


#------------------------------------------------------------------------------
# Subscription Expression
#------------------------------------------------------------------------------
class _ImplicitAttributeBinder(object):
    """ A thin class which supports attaching a notifier to an implicit
    attribute lookup.

    """
    # This doesn't need to be provided as a monitor because implicit 
    # attribute lookups, when successful, will always be on an instance
    # of BaseComponent and should never need to be hooked by an Enaml 
    # extension.
    def __init__(self, parent):
        """ Initialize an _ImplicitAttributeBinder

        Parameters
        ----------
        parent : SubscriptionExpression
            The parent SubscriptionExpression instance. Only a weak
            reference to the parent is stored.

        """
        self.parent_ref = ref(parent)
    
    def __call__(self, obj, name):
        """ Binds the change handler to the given object/attribute
        pair, provided the attribute points to a valid trait.

        Parameters
        ----------
        obj : BaseComponent
            The BaseComponent instance that owns the attribute.
        
        name : string
            The attribute name of interest
             
        """
        trait = obj.trait(name)
        if trait is not None and trait is not Disallow:
            obj.on_trait_change(self.notify, name)
    
    def notify(self):
        """ The trait change handler callback. It calls the monitor
        changed method on the parent when the trait changes, provided 
        the parent has not already been garbage collected.
        
        """
        parent = self.parent_ref()
        if parent is not None:
            parent._on_monitor_changed()


class SubscriptionExpression(AbstractExpression):
    """ A concrete implementation of AbstractExpression. An instance 
    of SubcriptionExpression emits the expression_changed signal when
    the value of the underlying expression changes. It does not 
    support notification.

    """
    def __init__(self, monitor_classes, *args):
        """ Initialize a SubscriptionExpression

        Parameters
        ----------
        monitor_classes : iterable of AbstractMonitor subclasses
            An iterable of AbstractMonitor subclasses which will
            be used to generating the monitoring code for the
            expression.
        
        *args
            The arguments required to initialize an AbstractExpression
        
        """
        super(SubscriptionExpression, self).__init__(*args)
        
        # Create the monitor instances and connect their signals
        monitors = []
        handler = self._on_monitor_changed
        for mcls in monitor_classes:
            if not issubclass(mcls, AbstractMonitor):
                msg = ('Monitors must be subclasses of AbstractMonitor. '
                       'Got %s instead.')
                raise TypeError(msg % mcls)
            monitor = mcls()
            monitor.expression_changed.connect(handler)
            monitors.append(monitor)

        # Collect the generated code from the monitors that will be
        # inserted into the code for the expression.
        bp_code = Code.from_code(self.code)
        code_list = list(bp_code.code)
        insertions = defaultdict(list)
        for monitor in monitors:
            for idx, code in monitor.get_insertion_code(code_list):
                insertions[idx].extend(code)
        
        # Create a new code list which interleaves the code generated
        # by the monitors at the appropriate location in the expression.
        new_code = []
        for idx, code_op in enumerate(code_list):
            if idx in insertions:
                new_code.extend(insertions[idx])
            new_code.append(code_op)
        
        bp_code.code = new_code
        self.eval_code = bp_code.to_code()
        self.monitors = tuple(monitors)
        self.implicit_binder = _ImplicitAttributeBinder(self)
        self.old_value = NotImplemented

    def _on_monitor_changed(self):
        """ The signal callback which is fired from a monitor when the
        expression changes. It will fire the expression_changed signal
        provided that the value of the expression has actually changed.

        """
        new_value = self.eval()
        
        # Guard against exceptions being raise during comparison, such 
        # as when comparing two numpy arrays.
        try:
            different = new_value != self.old_value
        except Exception:
            different = True

        if different:
            self.old_value = new_value
            self.expression_changed(self, self.name, new_value)

    def eval(self):
        """ Evaluates the expression and returns the result. It also
        resets the monitors before evaluating the expression to help
        ensures that duplicate notifications are avoided.

        """
        # Reset the monitors before every evaluation so that any old 
        # notifiers are disconnected. This avoids muti-notifications.
        self.implicit_binder = binder = _ImplicitAttributeBinder(self)
        for monitor in self.monitors:
            monitor.reset()

        obj = self.obj_ref()
        if obj is None:
            return NotImplemented
        
        identifiers = self.identifiers
        f_globals = self.f_globals
        toolkit = self.toolkit
        overrides = {'nonlocals': NonlocalScope(obj, binder)}
        scope = ExecutionScope(
            obj, identifiers, f_globals, toolkit, overrides, binder,
        )

        with toolkit:
            res = eval(self.eval_code, f_globals, scope)

        return res

    def notify(self, old, new):
        """ A no-op notification method since SubscriptionExpression does
        not support notification.

        """
        pass


#------------------------------------------------------------------------------
# Delegation Expression
#------------------------------------------------------------------------------
class DelegationExpression(SubscriptionExpression):
    """ A SubscriptionExpression subclass that adds notification support
    by setting the value on the contituents of the expression according
    to any provide inverters.

    """
    def __init__(self, inverter_classes, *args):
        """ Initialize a DelegationExpression

        Parameters
        ----------
        inverter_classes : iterable of AbstractInverter subclasses
            An iterable of concrete AbstractInverter subclasses which
            will invert the given expression code into a mirrored 
            operation which sets the value on the appropriate object.
        
        *args
            The arguments required to initialize a SubscriptionExpression
        
        """
        super(DelegationExpression, self).__init__(*args)
        
        inverters = []
        bp_code = Code.from_code(self.code)
        code_list = bp_code.code

        for inv_cls in inverter_classes:
            inverter = inv_cls()
            new_code = inverter.get_inverted_code(code_list)
            if new_code is not None:
                bp_code.code = new_code
                inverters.append(bp_code.to_code())
        
        if not inverters:
            msg = ("Unable to delegate expression to the '%s' attribute of "
                   "the %s object. The provided expression is not structured "
                   "in a way which is suitable for delegation by any of "
                   "the supplied code inverters.")
            raise ValueError(msg % (self.name, self.obj_ref()))

        self.inverters = inverters
    
    def notify(self, old, new):
        """ A notification method which runs through the list of inverted
        code objects which attempt to set the value. The process stops on
        the first successful inversion. If none of the invertors are 
        successful, a RuntimeError is raised.

        """
        obj = self.obj_ref()
        if obj is None:
            return
        
        # We don't need to attempt the inversion if the new value
        # is the same as the last value generated by the expression.
        # This helps prevent bouncing back and forth which can be
        # induced by excessive notification. Guard against exceptions
        # being raise during comparison, such as when comparing two
        # numpy arrays.
        try:
            different = new != self.old_value
        except Exception:
            different = True

        if not different:
            return

        # The override dict is populated with information about the
        # expression and the change. The values allow the generated
        # inverter codes to access the information which is required
        # to perform the operation. The items are added using names
        # which are not valid Python identifiers and therefore do
        # not risk clashing with names in the expression. This is
        # the same technique used by the Python interpreter itself.
        identifiers = self.identifiers
        f_globals = self.f_globals
        toolkit = self.toolkit
        overrides = {
            '_[expr]': self, '_[obj]': obj, '_[old]': old, '_[new]': new, 
            '_[name]': self.name, 'nonlocals': NonlocalScope(obj, None),
        }
        scope = ExecutionScope(
            obj, identifiers, f_globals, toolkit, overrides, None,
        )

        # Run through the inverters, giving each a chance to do the
        # inversion. The process ends with the first success. If 
        # none of the invertors are successful an error is raised.
        with toolkit:
            for inverter in self.inverters:
                if eval(inverter, f_globals, scope):
                    break
            else:
                msg = ("Unable to delegate expression to the '%s' attribute "
                       "of the %s object. None of the provided inverters were "
                       "successful in assigning the value.")
                raise RuntimeError(msg)

