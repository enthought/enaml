#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import MetaHasTraits, Property, Disallow,  Instance, Str

from .dynamic_scope import DynamicAttributeError
from .exceptions import DeclarativeNameError, OperatorLookupError
from .object import Object, ObjectData
from .object_property import ObjectProperty, ReadOnlyObjectProperty, Undefined
from .operator_context import OperatorContext
from .trait_types import EnamlInstance, EnamlEvent


#------------------------------------------------------------------------------
# UserAttribute and UserEvent
#------------------------------------------------------------------------------
class UserAttribute(EnamlInstance):
    """ An EnamlInstance subclass which implements the `attr` keyword.

    """
    def get(self, obj, name):
        """ The trait getter method.

        This returns the value from the object's dict, or raises an
        uninitialized error if the value doesn't exist.

        """
        dct = obj.__dict__
        if name not in dct:
            self.uninitialized_error(obj, name)
        return dct[name]

    def set(self, obj, name, value):
        """ The trait setter method.

        This sets the value in the object's dict if it is valid, and
        emits a change notification if the value has changed. The first
        time the value is set the change notification will carry None
        as the old value.

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
        """ Raise a DynamicAttributeError for an object and attr name.

        """
        msg = "cannot access the uninitialized '%s' attribute of the %s object"
        raise DynamicAttributeError(msg % (name, obj))


class UserEvent(EnamlEvent):
    """ An EnamlEvent subclass which implements the `event` keyword.

    This subclass contains no additional logic. Its type is simply used
    to distinguish between events declared by the framework, and events
    declared by the user.

    """
    pass


#------------------------------------------------------------------------------
# Declarative Helpers
#------------------------------------------------------------------------------
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


def setup_bindings(instance, bindings, identifiers, f_globals):
    """ Setup the expression bindings for a declarative instance.

    Parameters
    ----------
    instance : Declarative
        The declarative instance which owns the bindings.

    bindings : list
        A list of binding dicts created by the enaml compiler.

    identifiers : dict
        The identifiers scope to associate with the bindings.

    f_globals : dict
        The globals dict to associate with the bindings.

    """
    operators = instance.operators
    for binding in bindings:
        opname = binding['operator']
        try:
            operator = operators[opname]
        except KeyError:
            filename = binding['filename']
            lineno = binding['lineno']
            block = binding['block']
            raise OperatorLookupError(opname, filename, lineno, block)
        operator(instance, binding['name'], binding['func'], identifiers)


#------------------------------------------------------------------------------
# Declarative
#------------------------------------------------------------------------------
class DeclarativeMeta(MetaHasTraits):
    """ The metaclass for declarative classes.

    This metaclass collects the declarative properties declared on the
    classes and adds them to the `_declarative_properties` set for the
    class.

    """
    def __new__(meta, name, bases, dct):
        cls = MetaHasTraits.__new__(meta, name, bases, dct)
        properties = set()
        for key, value in cls.__class_traits__.iteritems():
            if isinstance(value.trait_type, DeclarativeProperty):
                properties.add(key)
            cls._declarative_properties = properties
        return cls


class DeclarativeData(ObjectData):
    """ An ObjectData subclass which adds room for declarative storage.

    """
    __slots__ = ('operators', 'expressions', 'listeners')

    def data_changed(self, owner, name, old, new):
        """ Handle the data change notification on the declarative data.

        This will run the listeners attached to the owner.

        """
        owner.run_listeners(name, old, new)


class DeclarativeProperty(ObjectProperty):
    """ An ObjectProperty subclass for declarative properties.

    A DeclarativeProperty has the ability to pull its default from a
    bound expressions.

    """
    def get_default(self, owner, name):
        """ Get the default value for the property.

        A declarative property first tries to retrieve the default from
        a bound expression object, failing back to the superclass logic
        on failure.

        """
        value = owner.eval_expression(name)
        if value is NotImplemented:
            value = super(DeclarativeProperty, self).get_default(owner, name)
        return value
        # try:
        #     return obj.eval_expression(name)
        # except DynamicAttributeError:
        #     raise  # Reraise a propagating initialization error.
        # except Exception:
        #     import traceback
        #     # XXX I'd rather not have to break into the private api here.
        #     expr = _find_expression(obj, name)
        #     if expr is None:
        #         filename = '<unknown>'
        #         lineno = -1
        #     else:
        #         filename = expr._func.func_code.co_filename
        #         lineno = expr._func.func_code.co_firstlineno
        #     args = (filename, lineno, traceback.format_exc())
        #     msg = ('Error initializing expression (%r line %s). Orignal '
        #            'exception was:\n%s')
        #     raise DynamicAttributeError(msg % args)


class Declarative(Object):
    """ The most base class of the Enaml declarative objects.

    This class provides the core functionality required of declarative
    Enaml types. It can be used directly in a declarative Enaml object
    tree to store and react to state changes. It has no concept of a
    visual representation; that functionality is added by subclasses.

    """
    __metaclass__ = DeclarativeMeta

    #: Redefine the name attribute as a DeclarativeProperty so that
    #: it can be initialized with the declarative enaml syntax.
    name = DeclarativeProperty(Str, default='')

    #: A readonly property which returns the current instance of the
    #: component. This allows declarative Enaml expressions to access
    #: 'self' according to Enaml's dynamic scoping rules.
    self = Property(fget=lambda self: self)

    #: The operator context used to build out this instance. This is
    #: assigned during object instantiation. It should not be edited
    #: by user code.
    operators = ReadOnlyObjectProperty('operators')

    _object_data = Instance(DeclarativeData, ())

    #: A private class set of declarative property names. This is filled
    #: by the metaclass.
    _declarative_properties = set(['name'])

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
        super(Declarative, self).__init__(parent, **kwargs)
        self._object_data.operators = OperatorContext.active_context()

    #--------------------------------------------------------------------------
    # Declarative API
    #--------------------------------------------------------------------------
    def populate(self, description, identifiers, f_globals):
        """ Populate this declarative instance from a description.

        This method is called when the object was created from within
        a declarative context. In particular, there are two times when
        it may be called:

            - The first is when a type created from the `enamldef`
              keyword is instatiated; in this case, the method is
              invoked by the EnamlDef metaclass.

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

        Notes
        -----
        The caller of this method should enter the child event context
        of the instance before invoking the method. This reduces the
        number of child events which are generated during startup.

        """
        ident = description['identifier']
        if ident:
            identifiers[ident] = self
        bindings = description['bindings']
        if len(bindings) > 0:
            setup_bindings(self, bindings, identifiers, f_globals)
        children = description['children']
        if len(children) > 0:
            for child in children:
                cls = scope_lookup(child['type'], f_globals, child)
                instance = cls(self)
                with instance.children_event_context():
                    instance.populate(child, identifiers, f_globals)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @classmethod
    def _add_user_attribute(cls, name, attr_type, is_event):
        """ A private classmethod used by the Enaml compiler machinery.

        This method is used to add user attributes and events to custom
        derived enamldef classes. If the attribute already exists on the
        class and is not a user defined attribute, an exception will be
        raised. The only method of overriding standard trait attributes
        is through traditional subclassing.

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
            if trait_type is not Disallow:
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
    def bind_expression(self, expression):
        """ Bind an expression to the object.

        This method can be called to bind a value-providing expression
        to the object. If the named attribute for the expression does
        not exist, an exception is raised.

        Parameters
        ----------
        expression : AbstractExpression
            A concrete implementation of AbstractExpression. This value
            is not type checked for performance reasons. It is assumed
            that the caller provides a correct value.

        """
        if expression.name not in self._declarative_properties:
            msg = "Cannot bind expression. '%s' is not a declarative property "
            msg += "on the %s object."
            raise AttributeError(msg % (expression.name, self))
        # All expressions are added, even if they override an old one.
        # When looking up an expression, it is done in reverse order
        # so that the most recently bound expression is used.
        exprs = self._object_data.expressions
        if exprs is Undefined:
            exprs = self._object_data.expressions = []
        exprs.append(expression)

    def bind_listener(self, listener):
        """ A private method used by the Enaml execution engine.

        This method is called by the Enaml operators to bind the given
        listener to the object. If the named attribute for the listener
        does not exist, an exception is raised.

        Parameters
        ----------
        listener : AbstractListener
            A concrete implementation of AbstractListener. This value
            is not type checked for performance reasons. It is assumed
            that the caller provides a correct value.

        """
        if listener.name not in self._declarative_properties:
            msg = "Cannot bind listener. '%s' is not a declarative property "
            msg += "on the %s object."
            raise AttributeError(msg % (listener.name, self))
        listeners = self._object_data.listeners
        if listeners is Undefined:
            listeners = self._object_data.listeners = []
        listeners.append(listener)

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
        # Find the expression in reverse order, using the most recently
        # bound expression first.
        found = None
        exprs = self._object_data.expressions
        if exprs is not Undefined:
            for expr in reversed(exprs):
                if expr.name == name:
                    found = expr
                break
        if found is not None:
            return found.eval(self, name)
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
        listeners = self._object_data.listeners
        if not listeners:
            return
        for listener in listeners:
            if listener.name == name:
                listener.value_changed(self, name, old, new)

