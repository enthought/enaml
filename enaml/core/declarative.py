#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, List, Property, Str, Dict, Disallow

from .expressions import AbstractExpression
from .object import Object
from .operator_context import OperatorContext
from .trait_types import ExpressionTrait, UserAttribute, UserEvent


#: The traits types on an Declarative instance which can be overridden
#: by the user in an enamldef declaration.
_OVERRIDE_ALLOWED = (UserAttribute, UserEvent)


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

    #: The private dictionary of expression objects that are bound to
    #: attributes on this component. It should not be manipulated by
    #: user code. Rather, expressions should be bound by the operators
    #: by calling the '_bind_expression' method.
    _expressions = Dict(Str, List(Instance(AbstractExpression)))

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
        # do not override the keywords. The builders appear and are run
        # in the reverse order of a typical mro. The most base builder
        # gets to add its children and bind its expressions first.
        # Builders that come later can then override these bindings.
        # Each component gets it's own identifier namespace and current
        # operator context.
        if self._builders:
            identifiers = {}
            operators = OperatorContext.active_context()
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
            if not isinstance(ttype, _OVERRIDE_ALLOWED):
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
        cls.__base_traits__[name] = ctrait
        cls.__class_traits__[name] = ctrait

    def _bind_expression(self, name, expression, notify_only=False):
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

        notify_only : bool, optional
            If True, the expression is only a notifier, in which case
            multiple binding is allowed, otherwise the new expression
            overrides any old non-notify expression. Defaults to False.

        """
        curr = self.trait(name)
        if curr is None or curr.trait_type is Disallow:
            msg = "Cannot bind expression. %s object has no attribute '%s'"
            raise AttributeError(msg % (self, name))

        # If this is the first time an expression is being bound to the
        # given attribute, then we hook up a change handler. This ensures
        # that we only get one notification event per bound attribute.
        # We also create the notification entry in the dict, which is
        # a list with at least one item. The first item will always be
        # the left associative expression (or None) and all following
        # items will be the notify_only expressions.
        expressions = self._expressions
        if name not in expressions:
            self.on_trait_change(self._on_bound_attr_changed, name)
            expressions[name] = [None]

        # There can be multiple notify_only expressions bound to a
        # single attribute, so they just get appended to the end of
        # the list. Otherwise, the left associative expression gets
        # placed at the zero position of the list, overriding any
        # existing expression.
        if notify_only:
            expressions[name].append(expression)
        else:
            handler = self._on_expression_changed
            old = expressions[name][0]
            if old is not None:
                old.expression_changed.disconnect(handler)
            expression.expression_changed.connect(handler)
            expressions[name][0] = expression

            # Hookup support for default value computation. We only need
            # to add an ExpressionTrait once, since it will reach back
            # into the _expressions dict as needed and retrieve the most
            # current bound expression.
            if not isinstance(curr.trait_type, ExpressionTrait):
                self.add_trait(name, ExpressionTrait(curr))

    def _on_expression_changed(self, expression, name, value):
        """ A private signal callback for the expression_changed signal
        of the bound expressions. It updates the value of the attribute
        with the new value from the expression.

        """
        setattr(self, name, value)

    def _on_bound_attr_changed(self, obj, name, old, new):
        """ A private handler which is called when any attribute which
        has a bound signal changes. It calls the notify method on each
        of the expressions bound to that attribute, but if the component
        is marked as live.

        """
        # The check for None is for the case where there are no left
        # associative expressions bound to the attribute, so the first
        # entry in the list is still None.
        for expr in self._expressions[name]:
            if expr is not None:
                expr.notify(old, new)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def destroy(self):
        """ A reimplement parent class destructor method.

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

