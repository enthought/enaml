#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty

from atom.api import Member, ReadOnly, UserMember, Value, Str, null

from .dynamic_scope import DynamicAttributeError
from .exceptions import DeclarativeNameError, OperatorLookupError
from .object import Object
from .operator_context import OperatorContext


def scope_lookup(name, scope, description):
    """ A function which retrieves a name from a scope.

    If the lookup fails, a DeclarativeNameError is raised. This can
    be used to lookup names for a description dict from a global scope
    with decent error reporting when the lookup fails.

    Parameters
    ----------
    name : str
        The name to retreive from the scope.

    scope : mapping
        A mapping object.

    description : dict
        The description dictionary associated with the lookup.

    """
    try:
        item = scope[name]
    except KeyError:
        lineno = description['lineno']
        filename = description['filename']
        block = description['block']
        raise DeclarativeNameError(name, filename, lineno, block)
    return item


class DeclarativeExpression(object):
    """ An interface for defining declarative expressions.

    Then Enaml operators are responsible for assigning an expression to
    the data struct of the relevant `DeclarativeProperty`.

    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """ Get the name to which the expression is bound.

        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, owner):
        """ Evaluate and return the results of the expression.

        Parameters
        ----------
        owner : Declarative
            The declarative object which owns the expression.

        """
        raise NotImplementedError


class DeclarativeProperty(UserMember):
    """ An atom `Member` which enables data binding in Enaml.

    A declarative property is used to wrap another member on an Atom
    subclass to enable that member to be bound by Enaml syntax.

    """
    __slots__ = 'member'

    def __init__(self, member=Member()):
        """ Initialize a DeclarativeProperty.

        Parameters
        ----------
        member : Member, optional
            The atom member to use for validation and default value
            handling. The default is a `Member` member.

        """
        assert isinstance(member, Member), "member must be an atom 'Member'"
        super(DeclarativeProperty, self).__init__()
        self.member = member

    def _set_member_name(self, name):
        """ Assign the name to this member.

        This method is called by the Atom metaclass when a class is
        created. This makes sure the name of the internal member is
        also updated.

        """
        super(DeclarativeProperty, self)._set_member_name(name)
        self.member._set_member_name(name)

    def _set_member_index(self, index):
        """ Assign the index to this member.

        This method is called by the Atom metaclass when a class is
        created. This makes sure the index of the internal member is
        also updated.

        """
        super(DeclarativeProperty, self)._set_member_index(index)
        self.member._set_member_index(index)

    def clone(self):
        """ Create a clone of the declarative property.

        """
        clone = super(DeclarativeProperty, self).clone()
        clone.member = self.member.clone()
        return clone

    def default(self, owner, name):
        """ Compute the default value for the declarative property.

        The default is retrieved first from a bound expression. If
        that succeeds, the value is validated using the internal
        member. Otherwise, the internal member provides the default.

        """
        value = owner.evaluate_expression(self.name)
        if value is not null:
            value = self.member.do_validate(owner, null, value)
        else:
            value = self.member.do_default(owner)
        return value

    def validate(self, owner, name, old, new):
        """ Validate the declarative property value.

        The validation is delegated to the internal member.

        """
        return self.member.do_validate(owner, old, new)


#: Export DeclarativeProperty as something a bit easier to type
d = DeclarativeProperty


class ExpressionNotifier(object):
    """ A simple notifier object used by Declarative.

    DeclarativeExpression objects which are bound to a declarative will
    use this notifier to notify the declarative when their expression
    is invalid and should be recomputed.

    """
    __slots__ = 'owner'

    def __init__(self, owner):
        """ Initialize an ExpressionNotifier.

        Parameters
        ----------
        owner : Declarative
            The declarative object which owns this notifier.

        """
        # The strong internal reference cycle is deliberate. It will be
        # cleared during the `destroy` method of the Declarative.
        self.owner = owner

    def __call__(self, name):
        """ Notify the declarative owner that the expression is invalid.

        Parameters
        ----------
        name : str
            The name of the expression which is invalid.

        """
        owner = self.owner
        if owner is not None:
            setattr(owner, name, owner.evaluate_expression(name))


class Declarative(Object):
    """ The most base class of the Enaml declarative objects.

    This class provides the core functionality required of declarative
    Enaml types. It can be used directly in a declarative Enaml object
    tree to store and react to state changes. It has no concept of a
    visual representation; that functionality is added by subclasses.

    """
    #: Redefine the 'name' attribute on Object as a 'd' property.
    name = d(Str())

    #: The operator context used to build out this instance. This is
    #: assigned during object instantiation.
    operators = ReadOnly()

    #: The list of value-providing bound expressions for the object.
    #: The operators will append expressions to this list as-needed.
    _expressions = Value(factory=list)

    #: An object which is used by the operators to notify this object
    #: when a bound expression has been invalidated. This should not
    #: be manipulated by user code.
    _expression_notifier = Value()

    def _default__expression_notifier(self):
        return ExpressionNotifier(self)

    #: Seed the class heirarchy with an empty descriptions tuple. The
    #: enaml compiler machinery will populate this for each enamldef.
    __declarative_descriptions__ = ()

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
        self.operators = OperatorContext.active_context()
        super(Declarative, self).__init__(parent, **kwargs)
        descriptions = self.__class__.__declarative_descriptions__
        if len(descriptions) > 0:
            # Each description is an independent `enamldef` block
            # which gets its own independent identifiers scope.
            for description, f_globals in descriptions:
                identifiers = {}
                self.populate(description, identifiers, f_globals)

    def destroy(self):
        """ An overridden destructor method for declarative cleanup.

        """
        del self._expressions
        self._expression_notifier.owner = None  # break the ref cycle
        del self._expression_notifier
        super(Declarative, self).destroy()

    def populate(self, description, identifiers, f_globals):
        """ Populate this declarative instance from a description.

        This method is called when the object was created from within
        a declarative context. In particular, there are two times when
        it may be called:

            - The first is when a type created from the `enamldef`
              keyword is instatiated; in this case, the method is
              invoked by the Declarative constructor.

            - The second occurs when the object is instantiated by
              its parent from within its parent's `populate` method.

        In the first case, the description dict will contain the key
        `enamldef: True`, indicating that the object is being created
        from a "top-level" `enamldef` block.

        In the second case, the dict will have the key `enamldef: False`
        indicating that the object is being populated as a declarative
        child of some other parent.

        Subclasses may reimplement this method to gain custom control
        over how the children for its instances are created.

        *** This method may be called multiple times ***

        Consider the following sample:

        enamldef Foo(PushButton):
            text = 'bar'

        enamldef Bar(Foo):
            fgcolor = 'red'

        enamldef Main(Window):
            Container:
                Bar:
                    bgcolor = 'blue'

        The instance of `Bar` which is created as the `Container` child
        will have its `populate` method called three times: the first
        to populate the data from the `Foo` block, the second to populate
        the data from the `Bar` block, and the third to populate the
        data from the `Main` block.

        Parameters
        ----------
        description : dict
            The description dictionary for the instance.

        identifiers : dict
            The dictionary of identifiers to use for the bindings.

        f_globals : dict
            The dictionary of globals for the scope in which the object
            was declared.

        """
        ident = description['identifier']
        if ident:
            identifiers[ident] = self
        bindings = description['bindings']
        if len(bindings) > 0:
            self.setup_bindings(bindings, identifiers, f_globals)
        children = description['children']
        if len(children) > 0:
            for child in children:
                cls = scope_lookup(child['type'], f_globals, child)
                instance = cls(self)
                instance.populate(child, identifiers, f_globals)

    def setup_bindings(self, bindings, identifiers, f_globals):
        """ Setup the expression bindings for the object.

        Parameters
        ----------
        bindings : list
            A list of binding dicts created by the enaml compiler.

        identifiers : dict
            The identifiers scope to associate with the bindings.

        f_globals : dict
            The globals dict to associate with the bindings.

        """
        operators = self.operators
        for binding in bindings:
            opname = binding['operator']
            try:
                operator = operators[opname]
            except KeyError:
                filename = binding['filename']
                lineno = binding['lineno']
                block = binding['block']
                raise OperatorLookupError(opname, filename, lineno, block)
            operator(self, binding['name'], binding['func'], identifiers)

    def evaluate_expression(self, name):
        """ Evaluate an expression bound to this declarative object.

        Parameters
        ----------
        name : str
            The name of the declarative property to which the expression
            is bound.

        Returns
        -------
        result : object or null
            The result of the evaluated expression, or null if there
            is no expression bound for the given name.

        """
        # The operators will append all expressions to this list, so
        # the list is iterated in reverse order to use the expression
        # which was most recently bound.
        for expression in reversed(self._expressions):
            if expression.name == name:
                return expression.evaluate(self)
        return null

