#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    Instance, List, Property, Str, Dict, Disallow, ReadOnly, TraitType,
)

from .abstract_expressions import AbstractExpression, AbstractListener
from .dynamic_scope import DynamicAttributeError
from .object import Object
from .operator_context import OperatorContext
from .trait_types import EnamlInstance, EnamlEvent


#------------------------------------------------------------------------------
# Expression Trait
#------------------------------------------------------------------------------
class ExpressionTrait(TraitType):
    """ A custom trait type which is used to help implement expression
    binding. Instances of this trait are added to an object, but swap
    themselves out and replace the old trait the first time they are
    accessed. This allows bound expressions to be initialized in the
    proper order without requiring an explicit initialization graph.

    """
    def __init__(self, old_trait):
        """ Initialize an expression trait.

        Parameters
        ----------
        old_trait : ctrait
            The trait object that the expression trait is temporarily
            replacing. When a 'get' or 'set' is triggered on this
            trait, the old trait will be restored and then the default
            value of the expression will be applied.

        """
        super(ExpressionTrait, self).__init__()
        self.old_trait = old_trait

    def swapout(self, obj, name):
        """ Restore the old trait onto the object. This method takes
        care to make sure that listeners are copied over properly.

        """
        # The default behavior of add_trait does *almost* the right
        # thing when it copies over notifiers when replacing the
        # existing trait. What it fails to do is update the owner
        # attribute of TraitChangeNotifyWrappers which are managing
        # a bound method notifier. This means that if said notifier
        # ever dies, it removes itself from the incorrect owner list
        # and it will be (erroneously) called on the next dispatch
        # cycle. The logic here makes sure that the owner attribute
        # of such a notifier is properly updated with its new owner.
        obj.add_trait(name, self.old_trait)
        notifiers = obj.trait(name)._notifiers(0)
        if notifiers is not None:
            for notifier in notifiers:
                if hasattr(notifier, 'owner'):
                    notifier.owner = notifiers

    def compute_default(self, obj, name):
        """ Returns the default value as computed by the most recently
        bound expression. If a value cannot be provided, NotImplemented
        is returned.

        """
        try:
            res = obj.eval_expression(name)
        except DynamicAttributeError:
            raise # Reraise a propagating initialization error.
        except Exception:
            # XXX hack! I'd rather not dig into Declarative's private api.
            import traceback
            expr = obj._expressions[name]
            filename = expr._func.func_code.co_filename
            lineno = expr._func.func_code.co_firstlineno
            args = (filename, lineno, traceback.format_exc())
            msg = ('Error initializing expression (%r line %s). Orignal '
                   'exception was:\n%s')
            raise DynamicAttributeError(msg % args)
        return res

    def get(self, obj, name):
        """ Handle computing the initial value for the expression trait.
        This method first restores the old trait, then evaluates the
        expression and sets the value on the trait quietly. It then
        performs a getattr to return the new value of the trait.

        """
        self.swapout(obj, name)
        val = self.compute_default(obj, name)
        if val is not NotImplemented:
            obj.trait_setq(**{name: val})
        return getattr(obj, name, val)

    def set(self, obj, name, val):
        """ Handle the setting of an initial value for the expression
        trait. This method first restores the old trait, then sets
        the value on that trait. In this case, the expression object
        is not needed.

        """
        self.swapout(obj, name)
        setattr(obj, name, val)


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

    #: The private dictionary of expression objects that are bound to
    #: attributes on this component. It should not be manipulated by
    #: user code. Rather, expressions should be bound by the operators
    #: by calling the '_bind_expression' method.
    _expressions = Dict(Str, Instance(AbstractExpression))

    #: The private dictionary of listener objects that are bound to
    #: attributes on this component. It should not be manipulated by
    #: user code. Rather, expressions should be bound by the operators
    #: by calling the '_bind_listener' method.
    _listeners = Dict(Str, List(Instance(AbstractListener)))

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
        self.trait_set(**kwargs)

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
        base_traits = cls.__base_traits__
        if name in base_traits:
            ttype = base_traits[name].trait_type
            if not isinstance(ttype, (UserAttribute, UserEvent)):
                msg = ("can't add '%s' attribute. The '%s' attribute on "
                       "enamldef '%s.%s' already exists.")
                items = (name, name, cls.__module__, cls.__name__)
                raise TypeError(msg % items)

        trait_attr_cls = UserEvent if is_event else UserAttribute
        try:
            user_trait = trait_attr_cls(attr_type)
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
        anytrait_handler = cls.__prefix_traits__.get('@')
        if anytrait_handler is not None:
            ctrait._notifiers(1).append(anytrait_handler)
        cls.__base_traits__[name] = ctrait
        cls.__class_traits__[name] = ctrait

    def _bind_expression(self, name, expression):
        """ A private method used by the Enaml execution engine.

        This method is called by the Enaml operators to bind the given
        expression object to the given attribute name. If the attribute
        does not exist, an exception is raised. A strong reference to
        the expression object is kept internally.

        Parameters
        ----------
        name : string
            The name of the attribute on which to bind the expression.

        expression : AbstractExpression
            A concrete implementation of AbstractExpression.

        """
        curr = self.trait(name)
        if curr is None or curr.trait_type is Disallow:
            msg = "Cannot bind expression. %s object has no attribute '%s'"
            raise AttributeError(msg % (self, name))

        exprs = self._expressions
        handler = self._on_expr_invalidated
        if name in exprs:
            old = exprs[name]
            if old.invalidated is not None:
                old.invalidated.disconnect(handler)
        else:
            # Add support for default value computation. ExpressionTrait
            # must only be added once; it will call `eval_expression`
            # as needed and retrieve the most current expression value.
            if not isinstance(curr.trait_type, ExpressionTrait):
                self.add_trait(name, ExpressionTrait(curr))

        if expression.invalidated is not None:
            expression.invalidated.connect(handler)
        exprs[name] = expression

    def _bind_listener(self, name, listener):
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
            A concrete implementation of AbstractListener.

        """
        curr = self.trait(name)
        if curr is None or curr.trait_type is Disallow:
            msg = "Cannot bind listener. %s object has no attribute '%s'"
            raise AttributeError(msg % (self, name))
        lsnrs = self._listeners
        if name not in lsnrs:
            lsnrs[name] = []
        lsnrs[name].append(listener)

    def _on_expr_invalidated(self, name):
        """ A signal handler invoked when an expression is invalidated.

        This handler is connected to the `invalidated` signal on bound
        expressions which support dynamic notification. When a given
        expression is invalidated, it is recomputed and the value of
        its attribute is updated.

        Parameters
        ----------
        name : str
            The attribute name to which the invalid expression is bound.

        """
        value = self.eval_expression(name)
        if value is not NotImplemented:
            setattr(self, name, value)

    def _anytrait_changed(self, name, old, new):
        """ An any trait changed handler for listener notification.

        This handler will notify any bound listeners when their attribute
        of interest has changed. Using an `anytrait` handler reduces the
        number of notifier objects which must be created.

        """
        super(Declarative, self)._anytrait_changed(name, old, new)
        lsnrs = self._listeners
        if name in lsnrs:
            for listener in lsnrs[name]:
                listener.value_changed(self, name, old, new)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def eval_expression(self, name):
        """ Evaluate a bound expression with the given name.

        This will not update the value of the bound attribute.

        Parameters
        ----------
        name : str
            The name of the attribute to which the expression is bound.

        Returns
        -------
        result : object or NotImplemented
            The results of the expression, or NotImplemented if there
            is no expression bound to the given name.

        """
        exprs = self._expressions
        if name in exprs:
            return exprs[name].eval(self, name)
        return NotImplemented

    def destroy(self):
        """ A reimplemented parent class destructor method.

        This method clears the dictionary of bound expression objects
        before proceeding with the standard destruction.

        """
        self._expressions = {}
        super(Declarative, self).destroy()

    def when(self, switch):
        """ A method which returns `self` or None based on the truthness
        of the argument.

        This can be useful to easily turn off the effects of an object
        in various situations such as constraints-based layout.

        Parameters
        ----------
        switch : bool
            A boolean which indicates whether this instance or None
            should be returned.

        Returns
        -------
        result : self or None
            If 'switch' is boolean True, self is returned. Otherwise,
            None is returned.

        """
        if switch:
            return self

