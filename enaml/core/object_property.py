#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitType, Any
from traits.traits import trait_cast


#: A global sentinel object for representing undefined data.
Undefined = object()


class BaseObjectData(object):
    """ A base class for creating object data storage.

    This class works in concert with ObjectProperty to create trait
    objects with more space-efficient data storage. In most cases, a
    subclass needs only to declare the slots it will use for storage.

    """
    __slots__ = ()

    def __getattr__(self, name):
        """ Undefined and uninitialized attributes return NotIm

        """
        return Undefined

    def data_changed(self, owner, name, old, new):
        """ Called when the object data has changed.

        This method can be implemented in a subclass to be notified
        when the data in this object has changed. It will be called
        whenever an ObjectProperty is set with a new value, and that
        property's data notification flag is set to True. This can
        be much more efficient (in terms of space) than trait change
        notifiers.

        This will not be called the first time a data value is set.

        Parameters
        ----------
        owner : object
            The object which owns the object data.

        name : str
            The name of the data attribute which changed.

        old : object
            The old value of the data.

        new : object
            The new value of the data.

        """
        pass


class ReadOnlyObjectProperty(TraitType):
    """ A trait type which works with an object's ObjectData.

    The object must have an `_object_data` attribute which must be an
    instance of `BaseObjectData`.

    """
    def __init__(self, trait=Any, default=None, factory=None):
        """ Initialize a ReadOnlyObjectProperty.

        Parameters
        ----------
        trait : TraitHandler, optional
            The trait to use when validating the property.

        default : object, optional
            The default value to use for the property. The default is
            None.

        factory : callable, optional
            A callable factory which will generate the default value.
            If this is provided, the `default` will be ignored. The
            default is None.

        """
        super(ReadOnlyObjectProperty, self).__init__()
        self._trait = trait_cast(trait)
        self._default = default
        self._factory = factory

    def get(self, owner, name):
        """ The data getter for the object property.

        """
        value = getattr(owner._object_data, name)
        if value is Undefined:
            value = self.get_default(owner, name)
            setattr(owner._object_data, name, value)
        return value

    def get_default(self, owner, name):
        """ Lookup the default value for the property.

        This may be reimplemented by subclasses for more control.

        """
        factory = self._factory
        if factory is not None:
            value = factory()
        else:
            value = self._default
        return value


class ObjectProperty(ReadOnlyObjectProperty):
    """ A trait type which works with an object's ObjectData.

    The object must have an `_object_data` attribute which must be an
    instance of `BaseObjectData`.

    """
    def __init__(self, trait=Any, default=None, factory=None,
                 trait_notify=True, data_notify=True):
        """ Initialize an ObjectProperty.

        Parameters
        ----------
        trait : TraitHandler, optional
            The trait to use when validating the property.

        default : object, optional
            The default value to use for the property. The default is
            None.

        factory : callable, optional
            A callable factory which will generate the default value.
            If this is provided, the `default` will be ignored. The
            default is None.


        trait_notify : bool, optional
            Whether to fire a trait change notification when the
            property is changed. The default is True.

        data_notify : bool, optional
            Whether to call the `data_changed` method on the object
            data  when the property is changed. The default is True.

        """
        super(ObjectProperty, self).__init__(trait)
        self._trait_notify = trait_notify
        self._data_notify = data_notify

    def set(self, owner, name, value):
        """ The data setter for the object property.

        """
        value = self._trait.validate(owner, name, value)
        object_data = owner._object_data
        old = getattr(object_data, name)
        setattr(object_data, name, value)
        if old is not Undefined and old != value:
            if self._trait_notify:
                owner.trait_property_changed(name, old, value)
            if self._data_notify:
                object_data.data_changed(owner, name, old, value)

