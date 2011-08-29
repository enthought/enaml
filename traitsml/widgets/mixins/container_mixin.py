from traits.api import HasTraits, List, Either

from ..i_container import IContainer
from ..i_element import IElement
from ..i_component import IComponent


class ContainerMixin(HasTraits):
    """ A mixin class for container objects.
    
    This mixin class provides some common toolkit independent base
    handling of IContainer objects required by the IContainer interface.
    Namely, it manages the validation aspect of adding and removing
    children. If the operations are valid, then they are dispatched
    to methods to be implemented by subclasses.
    
    Attributes
    ----------
    _children = List(IComponent)
        The internal list of children for the container.

    Methods
    -------
    add_child(child)
        See IContainer.add_child

    remove_child(child)
        See IContainer.remove_child
    
    replace_child(child)
        See IContainer.replace_child
    
    children()
        See IContainer.children

    Notes
    -----
    These methods perform O(n) operations when checking the children.
    It is expected that the number of children will be small on average
    and so won't pose a problem. We could maintain a seperate set of
    children to do O(1) membership tests, but we want to keep the 
    memory footprint small.
        
    """
    _children = List(IComponent)

    def add_child(self, child):
        """ Adds the child to the internal list of children.

        """
        if child in self._children:
            raise ValueError('Child already added to container.')
        self._children.append(child)
        self.do_add_child(child)
    
    def remove_child(self, child):
        """ Removes the child from the internal list of children.

        """
        try:
            idx = self._children.index(child)
        except IndexError:
            raise ValueError('Child not in container.')

        del self._children[idx]
        self.do_remove_child(child, idx)

    def replace_child(self, child, other_child):
        """ Replaces a child in the internal list of children.

        """
        try:
            idx = self._children.index(child)
        except IndexError:
            raise ValueError('Child not in container.')
        
        if other_child in self._children:
            raise ValueError('Other child already in container.')
        
        self._children[idx] = other_child
        self.do_replace_child(child, other_child, idx)

    def children(self):
        """ Returns an iterator of the internal children.

        """
        return iter(self._children)

    def do_add_child(self, child):
        """ A method to be implemented by subclasses to add a child
        to their widget. This will be called only after 'add_child'
        has confirmed it is a valid operation.

        """
        raise NotImplementedError

    def do_remove_child(self, child, idx):
        """ A method to be implemented by subclasses to remove
        a child from their widget. This will be called only after 
        'remove_child' has confirmed it is a valid operation.

        """
        raise NotImplementedError
    
    def do_replace_child(child, other_child, idx):
        """ A method to be implemented by subclasses to replace
        a child in their widget. This will be called only after 
        'replace_child' has confirmed it is a valid operation.

        """
        raise NotImplementedError

