#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitType, TraitError
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

    def full_info(self, obj, name, value):
        """ Overridden parent class method to compute an appropriate info
        string for use in error messages.

        """
        return 'emitted with an object of %s' % self.base_type


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

