from traits.api import HasTraits, List, Either

from ..i_container import IContainer
from ..i_element import IElement
from ..i_component import IComponent


class ContainerMixin(HasTraits):
    """ A mixin class for container objects.
    
    This mixin class provides some common toolkit independent base
    handling of IContainer objects required by the IContainer interface.
    
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
        
    """
    _children = List(IComponent)

    def add_child(self, child):
        if child in self._children:
            raise ValueError('Child already added to container.')
        self._children.append(child)
        self.do_add_child(child)
    
    def remove_child(self, child):
        try:
            idx = self._children.index(child)
        except IndexError:
            raise ValueError('Child not in container.')

        del self._children[idx]
        self.do_remove_child(child, idx)

    def replace_child(self, child, other_child):
        try:
            idx = self._children.index(child)
        except IndexError:
            raise ValueError('Child not in container.')
        
        if other_child in self._children:
            raise ValueError('Other child already in container.')
        
        self._children[idx] = other_child
        self.do_replace_child(child, other_child, idx)

    def children(self):
        return iter(self._children)

    def do_add_child(self, child):
        raise NotImplementedError

    def do_remove_child(self, child, idx):
        raise NotImplementedError
    
    def do_replace_child(child, other_child, idx):
        raise NotImplementedError

