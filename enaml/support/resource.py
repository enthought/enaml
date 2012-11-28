#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Dict, Str, Instance, TraitType

from enaml.core.object import Object


class ResourceID(TraitType):

    def __init__(self, name):
        super(ResourceID, self).__init__()
        self._name = name

    def get(self, obj, name):
        handle = getattr(obj, self._name)
        if handle is not None:
            return handle.get().object_id


class Resource(Object):
    """ The base class of Enaml resource objects.

    """
    #: Potential stubout of an object which can be set to encode
    #: data for transmission.
    encoder = None


class ResourceManager(HasTraits):
    """ An object for managing a collection of resources.

    """
    #: Private storage for the Resource instances.
    _items = Dict(Str, Resource)

    def __iter__(self):
        """ Get an iterator for the resources in the manager.

        """
        return self._items.itervalues()

    def get(self, name):
        """ Retrieve a resource from the manager.

        Parameters
        ----------
        name : str
            The name of the resource to retrieve.

        Returns
        -------
        result : Resource
            The named resource in the collection.

        Raises
        ------
        ValueError
            The named resource does not exist in the collection.

        """
        items = self._items
        if name in items:
            return items[name]
        resource = self.load(name)
        if resource is None:
            raise ValueError("resource '%s' does not exist" % name)
        items[name] = resource
        return resource

    def add(self, resource):
        """ Add a resource to the collection.

        Parameters
        ----------
        resource : Resource
            The resource instance to add to the collection.

        Raises
        ------
        ValueError
            A resource with the same name already exists.

        """
        items = self._items
        name = resource.name
        if name in items and items[name] is not resource:
            raise ValueError("resource '%s' already exists" % name)
        items[name] = resource

    def remove(self, name):
        """ Remove the resource with the given name.

        Parameters
        ----------
        name : str
            The name of the resource to remove.

        Raises
        ------
        ValueError
            The named resource does not exist.

        """
        items = self._items
        if name not in items:
            raise ValueError("resource '%s' does not exist" % name)
        del items[name]

    def get_handle(self, name):
        """ Get a deferred handle to the resource.

        Parameters
        ----------
        name : str
            The name of the resource for which to retrieve a handle.

        Returns
        -------
        result : ResourceHandle
            A deferred handle to the resource.

        """
        return ResourceHandle(manager=self, name=name)

    def load(self, name):
        """ Load the resource for the given name.

        This method will be called to retrieve the named resource if
        it is requested before being added to the manager. This method
        can be implemented by subclasses to support lazy loading. The
        default implementation of this method returns None.

        Parameters
        ----------
        name : str
            The name of the resource to load.

        Returns
        -------
        result : Resource or None
            The resource for the given name, or None if it cannot
            be loaded.

        """
        return None


class ResourceHandle(HasTraits):
    """ An object which is a deferred handle to a shared `Resource`.

    Instances of this class are created by calling `get_handle` on a
    `ResourceManager` instance.

    """
    #: The resource manager which owns the handle. This value set when
    #: the handle is created and should not be modified by user code.
    manager = Instance(ResourceManager)

    #: The name of the resource to which the handle is pointing. This
    #: value is set when the handle is created and should not be
    #: modified by user code.
    name = Str

    def get(self):
        """ Get the resource pointed to by this handle.

        Returns
        -------
        result : Resource
            The resource to which the handle is pointing.

        """
        return self.manager.get(self.name)

