#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any, Property, Uninitialized


class SlotData(object):
    """ A base class for creating slot data storage.

    """
    __slots__ = ()

    def __getattr__(self, name):
        """ Undefined attributes return `Uninitialized`.

        """
        return Uninitialized

    def notify(self, obj, name):
        """ Implement in a subclass for slot data change notification.

        """
        pass


def slot_data_getter(name, default=None):
    """ Construct a slot data getter function.

    Parameters
    ----------
    name : str
        The name of the attribute to retrieve on the SlotData.

    default : object, optional
        The default value to return if the attribute has not been
        initialized. This value will not be copied. The default is
        None.

    Returns
    -------
    result : FunctionType
        A function which can be used as an item data property getter.

    """
    def getter(self):
        value = getattr(self._slot_data, name)
        if value is Uninitialized:
            value = default
        return value
    return getter


def slot_data_setter(name, notify=True):
    """ Construct a slot data setter function.

    Parameters
    ----------
    name : str
        The name of the attribute to set on the SlotData.

    notify : bool, optional
        Whether the setter should call the `notify` method on the
        slot data when the data has changed.

    Returns
    -------
    result : FunctionType
        A function which can be used as an item data property setter.

    """
    def setter(self, value):
        slot_data = self._slot_data
        old = getattr(slot_data, name)
        setattr(slot_data, name, value)
        if old is not Uninitialized and old != value:
            self.trait_property_changed(name, old, value)
            if notify:
                slot_data.notify(self, name)
    return setter


def SlotDataProperty(name, trait=Any, default=None, notify=True):
    """ Create a trait Property which works with an object's SlotData.

    The object must have a `_slot_data` attribute which is an instance
    of `SlotData` for this property to function correctly.

    Parameters
    ----------
    name : str
        The item data attribute name on which this property operates.

    trait : TraitHandler, optional
        The trait to use when validating the property.

    default : object, optional
        The default value to use for the attribute. This value is not
        copied, and so should be a scalar type. The default is None.

    notify : bool, optional
        Wether to notifier the slot data when a value is changed. The
        default is True.

    Returns
    -------
    result : Property
        A new trait property.

    """
    getter = slot_data_getter(name, default)
    setter = slot_data_setter(name, notify)
    return Property(trait=trait, fget=getter, fset=setter)

