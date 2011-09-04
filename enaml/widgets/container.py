from traits.api import Instance, List, Either

from .component import Component, IComponentImpl
from .control import Control


ContainerChildTypes = Either(
    Instance('Container'), Instance('enaml.widgets.panel.Panel'), Instance(Control),
)


class IContainerImpl(IComponentImpl):
    pass


class Container(Component):
    """ The base container interface. 
    
    Containers are non-visible components that are responsible for 
    laying out and arranging their children.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IContainerImpl)

    children = List(ContainerChildTypes)

