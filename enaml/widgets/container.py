from traits.api import Instance, List, Either

from .component import Component, IComponentImpl
from .control import Control


ContainerChildTypes = Either(
    Instance('Container'), Instance('enaml.widgets.panel.Panel'), Instance(Control),
)


class IContainerImpl(IComponentImpl):
    
    def create_widget(self):
        raise NotImplementedError
    
    def initialize_widget(self):
        raise NotImplementedError

    def layout_child_widgets(self):
        raise NotImplementedError


class Container(Component):
    """ The base container interface. 
    
    Containers are non-visible components that are responsible for 
    laying out and arranging their children.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    _impl = Instance(IContainerImpl)

    children = List(ContainerChildTypes)

    def layout(self):
        """ Initialize and layout the container and it's children.

        This method should be called by the parent panel during
        its layout process.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        impl = self._impl
        impl.create_widget()
        for child in self.children:
            child.layout()
        impl.initialize_widget()
        impl.layout_child_widgets()
        self._hook_impl()

