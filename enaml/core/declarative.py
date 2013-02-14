#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from atom.api import Member, ReadOnly, MemberChange, null

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

    @abstractmethod
    def evaluate(self, owner):
        """ Evaluate and return the results of the expression.

        Parameters
        ----------
        owner : Declarative
            The declarative object which owns the expression.

        """
        raise NotImplementedError


class DeclarativeListener(object):
    """ An interface definition for creating property listeners.

    Then Enaml operators are responsible for assigning listeners to the
    data struct of the relevant `DeclarativeProperty`.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def property_changed(self, change):
        """ Called when the member on the object has changed.

        Parameters
        ----------
        change : MemberChange
            The change object for the property.

        """
        raise NotImplementedError


class DeclarativeDataStruct(object):
    """ A struct for storing declarative data for a property.

    This struct is used by `Declarative` and the Enaml operators to
    manage the bound expressions and listeners. User code should not
    directly interact with this class.

    """
    __slots__ = ('value', 'expression', 'listeners')


class DeclarativeProperty(Member):
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
        self.member = member

    def data_struct(self, owner):
        """ Get the data struct associated with the property.

        Parameters
        ----------
        owner : Declarative
            The declarative object which owns the data struct.

        Returns
        -------
        result : DeclarativeDataStruct
            The declarative data struct for the object.

        """
        value = self.getfast(owner)
        if isinstance(value, DeclarativeDataStruct):
            return value
        data = DeclarativeDataStruct()
        data.value = value
        data.expression = data.listeners = None
        self.setfast(owner, data)
        return data

    def __get__(self, owner, cls):
        """ Get the value for the declarative property.

        """
        if owner is None:
            return self
        name = self._name
        member = self.member
        data = value = self.getfast(owner)
        if isinstance(data, DeclarativeDataStruct):
            value = data.value
            if value is null:
                if data.expression is not null:
                    value = data.expression.evaluate(owner)
                    if member.has_validate:
                        value = member.validate(owner, name, null, value)
                    data.value = value
                elif member.has_default:
                    value = data.value = member.default(owner, name)
        elif data is null and member.has_default:
            value = member.default(owner, name)
            self.setfast(owner, value)
        return value

    def __set__(self, owner, value):
        """ Set the value for the declarative property.

        """
        name = self._name
        member = self.member
        old = self.getfast(owner)
        if isinstance(old, DeclarativeDataStruct):
            old_value = old.value
            if old_value == value:
                return
            if member.has_validate:
                value = member.validate(owner, name, old_value, value)
            if old_value != value:
                old.value = value
                change = None
                if old.listeners is not None:
                    change = MemberChange(owner, name, old_value, value)
                    for listener in old.listeners:
                        listener.property_changed(change)
                if owner.notifications_enabled(name):
                    if change is None:
                        change = MemberChange(owner, name, old_value, value)
                    owner.notify(change)
        else:
            if old == value:
                return
            if member.has_validate:
                value = member.validate(owner, name, old, value)
            if old != value:
                self.setfast(owner, value)
                if owner.notifications_enabled(name):
                    change = MemberChange(owner, name, old, value)
                    owner.notify(change)


#------------------------------------------------------------------------------
# Declarative
#------------------------------------------------------------------------------
class ExpressionNotifier(object):
    def __init__(self, owner):
        self.owner = owner
    def __call__(self, name):
        owner = self.owner
        prop = owner.lookup_member(name)
        data = prop.data_struct(owner)
        if data.expression is not null:
            value = data.expression.evaluate(owner)
            prop.__set__(owner, value)


class ExpressionNotifierFactory(Member):
    __slots__ = ()
    def __init__(self):
        self.has_default = True
    def default(self, owner, name):
        return ExpressionNotifier(owner)


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
    self = property(lambda self: self)

    #: The operator context used to build out this instance. This is
    #: assigned during object instantiation. It should not be edited
    #: by user code.
    operators = ReadOnly()

    notifier = ExpressionNotifierFactory()

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
        descriptions = self.__class__.__enamldef_descriptions__
        if len(descriptions) > 0:
            # Each description is an independent `enamldef` block
            # which gets its own independent identifiers scope.
            for description, f_globals in descriptions:
                identifiers = {}
                self.populate(description, identifiers, f_globals)

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

