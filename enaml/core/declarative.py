#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    Any, Property, Disallow, ReadOnly, CTrait, Instance, Uninitialized,
)

from .dynamic_scope import DynamicAttributeError
from .object import Object
from .operator_context import OperatorContext
from .trait_types import EnamlInstance, EnamlEvent


#------------------------------------------------------------------------------
# User Attribute and User Event
#------------------------------------------------------------------------------
class UserAttribute(EnamlInstance):
    """ An EnamlInstance subclass that is used to implement optional
    attribute typing when adding a new user attribute to an Enaml
    component.

    """
    def get(self, obj, name):
        """ The trait getter method. Returns the value from the object's
        dict, or raises an uninitialized error if the value doesn't exist.

        """
        dct = obj.__dict__
        if name not in dct:
            self.uninitialized_error(obj, name)
        return dct[name]

    def set(self, obj, name, value):
        """ The trait setter method. Sets the value in the object's
        dict if it is valid, and emits a change notification if the
        value has changed. The first time the value is set the change
        notification will carry None as the old value.

        """
        value = self.validate(obj, name, value)
        dct = obj.__dict__
        if name not in dct:
            old = None
        else:
            old = dct[name]
        dct[name] = value
        if old != value:
            obj.trait_property_changed(name, old, value)

    def uninitialized_error(self, obj, name):
        """ A method which raises a DynamicAttributeError for the given
        object and attribute name.

        """
        msg = "Cannot access the uninitialized '%s' attribute of the %s object"
        raise DynamicAttributeError(msg % (name, obj))


class UserEvent(EnamlEvent):
    """ A simple EnamlEvent subclass used to distinguish between events
    declared by the framework, and events declared by the user.

    """
    pass


#------------------------------------------------------------------------------
# Declarative
#------------------------------------------------------------------------------
def _compute_default(obj, name):
    """ Compute the value for an expression.

    This is a private function used by Declarative to allow bound
    expression to provide default values for an attribute without
    requiring an explicit initialization graph.

    """
    try:
        return obj.eval_expression(name)
    except DynamicAttributeError:
        raise # Reraise a propagating initialization error.
    except Exception:
        import traceback
        expr = obj._expressions[name]
        filename = expr._func.func_code.co_filename
        lineno = expr._func.func_code.co_firstlineno
        args = (filename, lineno, traceback.format_exc())
        msg = ('Error initializing expression (%r line %s). Orignal '
               'exception was:\n%s')
        raise DynamicAttributeError(msg % args)


_quiet = set()
def _set_quiet(obj, name, value):
    """ Quietly set the named value on the object.

    This is a private function used by Declarative to allow bound
    expression to provide default values for an attribute without
    requiring an explicit initialization graph. It's a workaround
    for bug: https://github.com/enthought/traits/issues/26

    """
    q = _quiet
    owned = obj not in q
    if owned:
        obj._trait_change_notify(False)
        q.add(obj)
    setattr(obj, name, value)
    if owned:
        obj._trait_change_notify(True)
        q.discard(obj)


def _wired_getter(obj, name):
    """ The wired default expression getter.

    This is a private function used by Declarative to allow bound
    expression to provide default values for an attribute without
    requiring an explicit initialization graph.

    """
    itraits = obj._instance_traits()
    itraits[name] = itraits[name]._shadowed
    val = _compute_default(obj, name)
    if val is not NotImplemented:
        _set_quiet(obj, name, val)
    return getattr(obj, name, val)


def _wired_setter(obj, name, value):
    """ The wired default expression setter.

    This is a private function used by Declarative to allow bound
    expression to provide default values for an attribute without
    requiring an explicit initialization graph.

    """
    itraits = obj._instance_traits()
    itraits[name] = itraits[name]._shadowed
    setattr(obj, name, value)


def _wire_default(obj, name):
    """ Wire an expression trait for default value computation.

    This is a private function used by Declarative to allow bound
    expression to provide default values for an attribute without
    requiring an explicit initialization graph.

    """
    # This is a low-level performance hack that bypasses a mountain
    # of traits cruft and performs the minimum work required to make
    # traits do what we want.
    trait = CTrait(4)
    trait.property(_wired_getter, 2, _wired_setter, 3, None, 0)
    trait.handler = Any
    shadow = obj._trait(name, 2)
    trait._shadowed = shadow
    trait._notifiers = shadow._notifiers
    obj._instance_traits()[name] = trait


class ListenerNotifier(object):
    """ A lightweight trait change notifier used by Declarative.

    """
    def __call__(self, obj, name, old, new):
        """ Called by traits to dispatch the notifier.

        """
        if old is not Uninitialized:
            obj.run_listeners(name, old, new)

    def equals(self, other):
        """ Compares this notifier against another for equality.

        """
        return False

# Only a single instance of ListenerNotifier is needed.
ListenerNotifier = ListenerNotifier()


class Declarative(Object):
    """ The most base class of the Enaml declarative objects.

    This class provides the core functionality required of declarative
    Enaml types. It can be used directly in a declarative Enaml object
    tree to store and react to state changes. It has no concept of a
    visual representation; that functionality is added by subclasses.

    """
    #: A readonly property which returns the current instance of the
    #: component. This allows declarative Enaml expressions to access
    #: 'self' according to Enaml's dynamic scoping rules.
    self = Property(fget=lambda self: self)

    #: The operator context used to build out this instance. This is
    #: assigned during object instantiation. It should not be edited
    #: by user code.
    operators = ReadOnly

    #: The dictionary of bound expression objects. XXX These dicts are
    #: typically small and waste space. We need to switch to a more
    #: space efficient hash table at some point in the future. For
    #: pathological cases of large numbers of objects, the savings
    #: can be as high as 20%.
    _expressions = Instance(dict, ())

    #: The dictionary of bound listener objects. XXX These dicts are
    #: typically small and waste space. We need to switch to a more
    #: space efficient hash table at some point in the future. For
    #: pathological cases of large numbers of objects, the savings
    #: can be as high as 20%.
    _listeners = Instance(dict, ())

    #: A class attribute used by the Enaml compiler machinery to store
    #: the builder functions on the class. The functions are called
    #: when a component is instantiated and are the mechanism by which
    #: a component is populated with its declarative children and bound
    #: expression objects.
    _builders = []

    def __init__(self, parent=None, **kwargs):
        """ Initialize a declarative component.

        Parameters
        ----------
        parent : Object or None, optional
            The Object instance which is the parent of this object, or
            None if the object has no parent. Defaults to None.

        **kwargs
            Additional keyword arguments needed for initialization.

        """
        super(Declarative, self).__init__(parent)
        # If any builders are present, they need to be invoked before
        # applying any other keyword arguments so that bound expressions
        # do not override the keywords. The builders in the list exist
        # in the reverse order of a typical mro. The most base builder
        # gets to add its children and bind its expressions first.
        # Builders that come later can then override these bindings.
        # Each component gets it's own identifier namespace and current
        # operator context.
        operators = self.operators = OperatorContext.active_context()
        if self._builders:
            identifiers = {}
            for builder in self._builders:
                builder(self, identifiers, operators)

        # Apply the keyword arguments after the rest of the tree is
        # created. This makes sure that parameters passed in by the
        # user are not overridden by default expression bindings.
        # `trait_set` is slow, don't use it here.
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @classmethod
    def _add_user_attribute(cls, name, attr_type, is_event):
        """ A private classmethod used by the Enaml compiler machinery.

        This method is used to add user attributes and events to custom
        derived enamldef components. If the attribute already exists on
        the class and is not a user defined attribute, then an exception
        will be raised. The only method of overriding standard trait
        attributes is through traditional subclassing.

        Parameters
        ----------
        name : str
            The name of the attribute to add to the class.

        attr_type : type
            The type of the attribute.

        is_event : bool
            True if the attribute should be a UserEvent, False if it
            should be a UserAttribute.

        """
        class_traits = cls.__class_traits__
        if name in class_traits:
            trait_type = class_traits[name].trait_type
            if not isinstance(trait_type, (UserAttribute, UserEvent)):
                msg = ("can't add '%s' attribute. The '%s' attribute on "
                       "enamldef '%s.%s' already exists.")
                items = (name, name, cls.__module__, cls.__name__)
                raise TypeError(msg % items)

        trait_cls = UserEvent if is_event else UserAttribute
        try:
            user_trait = trait_cls(attr_type)
        except TypeError:
            msg = ("'%s' is not a valid type for the '%s' attribute "
                   "declaration on enamldef '%s.%s'")
            items = (attr_type, name, cls.__module__, cls.__name__)
            raise TypeError(msg % items)

        # XXX HasTraits.add_class_trait will raise an exception if the
        # the trait is already defined. There does not appear to be a
        # way to turn this off, nor does there appear to be a way to
        # formally remove a class trait. So, we just do what the traits
        # metaclass does when adding traits and directly add the ctrait
        # to the appropriate class dictionaries. The add_class_trait
        # classmethod does some extra work to make sure that the trait
        # is added to all subclasses, but that does not appear to be
        # needed in this case, since this method will only be called by
        # the compiler machinery for brand new subclasses.
        ctrait = user_trait.as_ctrait()
        class_traits[name] = ctrait
        cls.__base_traits__[name] = ctrait
        if '@' in cls.__prefix_traits__:
            anytrait_handler = cls.__prefix_traits__['@']
            ctrait._notifiers(1).append(anytrait_handler)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def bind_expression(self, name, expression):
        """ Bind an expression to the given attribute name.

        This method can be called to bind a value-providing expression
        to the given attribute name. If the named attribute does not
        exist, an exception is raised.

        Parameters
        ----------
        name : string
            The name of the attribute on which to bind the expression.

        expression : AbstractExpression
            A concrete implementation of AbstractExpression. This value
            is not type checked for performance reasons. It is assumed
            that the caller provides a correct value.

        """
        curr = self._trait(name, 2)
        if curr is None or curr.trait_type is Disallow:
            msg = "Cannot bind expression. %s object has no attribute '%s'"
            raise AttributeError(msg % (self, name))
        dct = self._expressions
        if name not in dct:
            _wire_default(self, name)
        dct[name] = expression

    def bind_listener(self, name, listener):
        """ A private method used by the Enaml execution engine.

        This method is called by the Enaml operators to bind the given
        listener object to the given attribute name. If the attribute
        does not exist, an exception is raised. A strong reference to
        the listener object is kept internally.

        Parameters
        ----------
        name : string
            The name of the attribute on which to bind the listener.

        listener : AbstractListener
            A concrete implementation of AbstractListener. This value
            is not type checked for performance reasons. It is assumed
            that the caller provides a correct value.

        """
        curr = self._trait(name, 2)
        if curr is None or curr.trait_type is Disallow:
            msg = "Cannot bind listener. %s object has no attribute '%s'"
            raise AttributeError(msg % (self, name))
        dct = self._listeners
        if name not in dct:
            dct[name] = [listener]
            self.add_notifier(name, ListenerNotifier)
        else:
            dct[name].append(listener)

    def eval_expression(self, name):
        """ Evaluate a bound expression with the given name.

        Parameters
        ----------
        name : str
            The name of the attribute with the bound expression.

        Returns
        -------
        result : object or NotImplemented
            The result of evaluating the expression, or NotImplemented
            if there is no expression bound to the given name.

        """
        dct = self._expressions
        if name in dct:
            return dct[name].eval(self, name)
        return NotImplemented

    def refresh_expression(self, name):
        """ Refresh the value of a bound expression.

        Parameters
        ----------
        name : str
            The attribute name to which the invalid expression is bound.

        """
        value = self.eval_expression(name)
        if value is not NotImplemented:
            setattr(self, name, value)

    def run_listeners(self, name, old, new):
        """ Run the listeners bound to the given attribute name.

        Parameters
        ----------
        name : str
            The name of the attribute with the bound listeners.

        old : object
            The old value to pass to the listeners.

        new : object
            The new value to pass to the listeners.

        """
        dct = self._listeners
        if name in dct:
            for listener in dct[name]:
                listener.value_changed(self, name, old, new)

