#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import WeakKeyDictionary, ref

from traits.api import TraitType, TraitError, BaseInstance
from traits.traits import CTrait


#------------------------------------------------------------------------------
# Enaml Instance
#------------------------------------------------------------------------------
class EnamlInstance(TraitType):
    """ A custom TraitType which serves as a simple isinstance(...)
    validator. This class serves as the base class for other custom
    trait types such as EnamlEvent and UserAttribute.

    """
    @staticmethod
    def is_valid_type(obj):
        """ A static method which returns whether or not the given object
        can be used as the type in an isinstance(..., type) expression.

        Paramters
        ---------
        obj : object
            The object which should behave like a type for the purpose
            of an isinstance check. This means the object is type
            or defines an '__instancecheck__' method.

        Returns
        -------
        result : bool
            True if the object is a type or defines a method named
            '__instancecheck__', False otherwise.

        """
        return isinstance(obj, type) or hasattr(obj, '__instancecheck__')

    def __init__(self, base_type=object):
        """ Initialize a UserAttribute instance.

        Parameters
        ----------
        base_type : type-like object, optional
            An object that behaves like a type for the purposes of a
            call to isinstance. The staticmethod 'is_valid_attr_type'
            defined on this class can be used to test a type before
            creating an instance of this class. It is assumed that the
            given type passes that test. The default is object.

        """
        if not EnamlInstance.is_valid_type(base_type):
            msg = '%s is not a valid type object'
            raise TypeError(msg % base_type)
        super(EnamlInstance, self).__init__()
        self.base_type = base_type

    def validate(self, obj, name, value):
        """ The validation handler for an EnamlInstace. It performs a 
        simple isinstance(...) check using the attribute type provided 
        to the constructor.

        """
        if not isinstance(value, self.base_type):
            self.error(obj, name, value)
        return value

    def full_info(self, obj, name, value):
        """ Overridden parent class method to compute an appropriate info
        string for use in error messages.

        """
        return 'an instance of %s' % self.base_type


#------------------------------------------------------------------------------
# Enaml Event
#------------------------------------------------------------------------------
class EnamlEventDispatcher(object):
    """ A thin object which is used to dispatch a notification for an
    EnamlEvent. Instances of this class are callable with at most one
    argument, which will be the payload of the event. Instances of this
    dispatcher should not be held onto, since they maintain a strong 
    reference to the underlying object.

    """
    def __init__(self, trait, obj, name):
        """ Initialize an event dispatcher.

        Parameters
        ----------
        trait : Instance(TraitType)
            The trait type instance on which validate will be called
            with the event payload.
        
        obj : Instance(HasTraits)
            The HasTraits object on which the event is being emitted.
        
        name : string
            The name of the event being emitted.
        
        """
        self._trait = trait
        self._obj = obj
        self._name = name
    
    def __call__(self, payload=None):
        """ Dispatches the event with the given payload.

        Paramters
        ---------
        payload : object, optional
            The payload argument of the event. This object will be 
            validated against the type declared for the event.
            The default payload is None.
        
        """
        obj = self._obj
        name = self._name
        self._trait.validate(obj, name, payload)
        obj.trait_property_changed(name, None, payload)


class EnamlEvent(EnamlInstance):
    """ A custom EnamlInstance that is used to implement the event
    type in Enaml. An EnamlEvent is read-only, and returns a dispatcher
    which can be called to emit the event.

    """
    def get(self, obj, name):
        """ The trait getter method. Returns an EnamlEventDispatcher
        instance which can be called to emit the event.

        """
        return EnamlEventDispatcher(self, obj, name)

    def set(self, obj, name, value):
        """ The trait setter method. Fires off a EnamlEventDispatcher
        as if the event were called with the payload.

        """
        EnamlEventDispatcher(self, obj, name)(value)

    def full_info(self, obj, name, value):
        """ Overridden parent class method to compute an appropriate info
        string for use in error messages.

        """
        return 'emitted with an object of %s' % self.base_type


#------------------------------------------------------------------------------
# Expression Trait
#------------------------------------------------------------------------------
class ExpressionInitializationError(Exception):
    """ An exception used to indicate an error during initialization
    of an expression.

    """
    # XXX - We can't inherit from AttributeError because the local 
    # scope object used by expressions captures an AttributeError
    # and converts it into in a KeyError in order to implement
    # dynamic attribute scoping. We actually want this exception
    # to propagate.
    pass


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
        res = NotImplemented
        expr = obj._expressions[name][0]
        if expr is not None:
            try:
                res = expr.eval()
            except Exception as e:
                # Reraise a propagating initialization error.
                if isinstance(e, ExpressionInitializationError):
                    raise
                msg = ('Error initializing expression (%r line %s). '
                       'Orignal exception was:\n%s')
                import traceback
                tb = traceback.format_exc()
                filename = expr.code.co_filename
                lineno = expr.code.co_firstlineno
                args = (filename, lineno, tb)
                raise ExpressionInitializationError(msg % args)
        return res

    def get(self, obj, name):
        """ Handle computing the initial value for the expression trait. 
        This method first restores the old trait, then evaluates the 
        expression and sets the value on the trait. It then performs
        a getattr to return the new value of the trait. If the object
        is not yet fully initialized, the value is set quietly.

        """
        self.swapout(obj, name)
        val = self.compute_default(obj, name)
        if val is not NotImplemented:
            if not obj.initialized:
                obj.trait_setq(**{name: val})
            else:    
                setattr(obj, name, val)
        return getattr(obj, name, val)

    def set(self, obj, name, val):
        """ Handle the setting of an initial value for the expression
        trait. This method first restores the old trait, then sets
        the value on that trait. In this case, the expression object
        is not needed. If the object is not yet fully initialized, the 
        value is set quietly.

        """
        self.swapout(obj, name)
        if not obj.initialized:
            obj.trait_setq(**{name: val})
        else:
            setattr(obj, name, val)


#------------------------------------------------------------------------------
# User Attribute and Event
#------------------------------------------------------------------------------
class UninitializedAttributeError(Exception):
    """ A custom Exception used by UserAttribute to signal the access 
    of an uninitialized attribute.

    """
    # XXX - We can't inherit from AttributeError because the local 
    # scope object used by expressions captures an AttributeError
    # and converts it into in a KeyError in order to implement
    # dynamic attribute scoping. We actually want this exception
    # to propagate.
    pass


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
        """ A method which raises an UninitializedAttributeError for
        the given object and attribute name

        """
        msg = "Cannot access the uninitialized '%s' attribute of the %s object"
        raise UninitializedAttributeError(msg % (name, obj))


class UserEvent(EnamlEvent):
    """ A simple EnamlEvent subclass used to distinguish between events
    declared by the framework, and events declared by the user.

    """
    pass


#------------------------------------------------------------------------------
# Bounded
#------------------------------------------------------------------------------
class Bounded(TraitType):
    """ Generic Bounded Trait class.

    The class defines a generic Trait where the value is validated
    on assigment to fall between low and high (static or dynamic) bounds.

    """
    info_text = "Bounded value"

    def __init__(self, value=None, low=None, high=None, **metadata):
        """
        Arguments
        ---------
        value :
            The default value. It can be a python object or a Trait.

        low :
            The lower bound of the Trait.

        high :
            The upper bound of the Trait.

        """
        if isinstance(value, CTrait):
            self.validate = self.validate_with_trait
            default_value = value.default
        else:
            self.validate = self.validate_bounds
            if value is None:
                if low is not None:
                    value = default_value = low
                else:
                    value = default_value = high
            else:
                default_value = value

        super(Bounded, self).__init__(default_value, **metadata)

        self._high = high
        self._low = low
        self._value = value

        if isinstance(value, basestring):
            self.default_value_type = 8
            self.default_value = self._get_default_value
    
    def _get_default_value(self, obj):
        """ Handles computing the default value for the Bounded trait.

        """
        return reduce(getattr, self._value.split('.'), obj)

    def validate_with_trait(self, obj, name, value):
        """ Validate the trait value.

        Validation takes place in two steps:
        #. The input value is validated based on the expected Trait type.
        #. The value it is between the static (or dynamic) bounds.

        """
        value_trait = self._value
        value = value_trait.validate(obj, name, value)
        return self.validate_bounds(obj, name, value)

    def validate_bounds(self, obj, name, value):
        """ Validate that the value is in range.

        .. note:: Any exceptions that may take place are converted to
            TraitErrors.

        """
        low, high = self.get_bounds(obj)
        if low is None:
            low = value
        if high is None:
            high = value
        
        is_inside_bounds = False
        try:
            is_inside_bounds = (low <= value <= high)
        except Exception as raised_exception:
            if isinstance(raised_exception, TraitError):
                raise raised_exception
            else:
                msg = ('Bound checking of {0} caused a the following Python '
                       'Exception: {1}'.format(value, raised_exception))
                raise TraitError(msg)
        
        if not is_inside_bounds:
            msg = ('The assigned date value must be bounded between {0} '
                   ' and {1}. Got {2} instead.'.format(low, high, value))
            raise TraitError(msg)

        return value

    def get_bounds(self, obj):
        """ Get the lower and upper bounds of the Trait.

        """
        low = self._low
        if isinstance(low, basestring):
            low = reduce(getattr, low.split('.'), obj)
        
        high = self._high
        if isinstance(high, basestring):
            high = reduce(getattr, high.split('.'), obj)

        return (low, high)


#------------------------------------------------------------------------------
# Lazy Property
#------------------------------------------------------------------------------
class LazyProperty(TraitType):
    """ A trait which behaves like a read-only cached property, but
    which lazily defers binding the dependency notifiers until the
    first time the value is retrieved. It is used to avoid situations
    where a property dependency in prematurely evaluated during
    component instantiation.

    """
    def __init__(self, trait=None, depends_on=''):
        """ Initialize a LazyProperty.

        Parameters
        ----------
        trait : TraitType, optional
            An optional trait type for the values returned by the
            property. List is required if using extending trait 
            name syntax for e.g. list listeners.
        
        depends_on : string, optional
            The traits notification string for the dependencies of
            the filter.
        
        """
        super(LazyProperty, self).__init__()
        self.dependency = depends_on
        self.handlers = WeakKeyDictionary()
        if trait is not None:
            self.default_value_type = trait.default_value_type

    def get(self, obj, name):
        """ Returns the (possibly cached) value of the filter. The 
        notification handlers will be attached the first time the
        value is accessed.

        """
        cache_name = '_%s_lazy_property_cache' % name
        dct = obj.__dict__
        if cache_name not in dct:
            method_name = '_get_%s' % name
            val = getattr(obj, method_name)()
            dct[cache_name] = val
            self.bind(obj, name)
        else:
            val = dct[cache_name]
        return val
    
    def bind(self, obj, name):
        """ Binds the dependency notification handlers for the object.

        """
        wr_obj = ref(obj)
        def notify():
            obj = wr_obj()
            if obj is not None:
                cache_name = '_%s_lazy_property_cache' % name
                old = obj.__dict__.pop(cache_name, None)
                obj.trait_property_changed(name, old)

        handlers = self.handlers
        dependency = self.dependency
        if obj in handlers:
            obj.on_trait_change(handlers[obj], dependency, remove=True)
        handlers[obj] = notify
        obj.on_trait_change(notify, dependency)


#------------------------------------------------------------------------------
# Coercing Instance
#------------------------------------------------------------------------------
class CoercingInstance(BaseInstance):
    """ A BaseInstance subclass which attempts to coerce a value by 
    calling the class constructor and passing the new value into the
    original validate method.

    """
    def validate(self, obj, name, value):
        """ Attempts to coerce the given value to an appropriate type
        by calling the underlying class constructor. The coerced value
        is then sent to the superclass' validate method.

        """
        if isinstance(self.klass, basestring):
            self.resolve_klass(obj, name, value)
        try:
            value = self.klass(value)
        except:
            pass
        return super(CoercingInstance, self).validate(obj, name, value)


#------------------------------------------------------------------------------
# Enaml Widget Instance
#------------------------------------------------------------------------------
class EnamlWidgetInstance(BaseInstance):
    """ A BaseInstance subclass which will call the 'setup' method on
    the value being assigned, passing in the appropriate toolkit widget
    object. The 'destroy' method on the old instance will be called 
    unless the 'destroy_old' flag is set to False. These operations are
    done *before* the value is actually set and therefore before any 
    change notifications are fired.

    """
    def __init__(self, *args, **kwargs):
        self.destroy_old = kwargs.pop('destroy_old', True)
        super(EnamlWidgetInstance, self).__init__(*args, **kwargs)

    def validate(self, obj, name, value):
        """ Validates the value using the superclass method. Upon
        success, it then destroys the old value (if requested) and 
        sets up the new value. The value is expected to be at least
        an instance WidgetComponent.

        """
        value = super(EnamlWidgetInstance, self).validate(obj, name, value)
        old = getattr(obj, name, None)
        if old is not None and self.destroy_old:
            old.destroy()
        value.setup(obj.toolkit_widget)
        return value

