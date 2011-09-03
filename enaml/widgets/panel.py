from traits.api import Instance, List

from .component import Component, IComponentImpl
from .container import Container


class IPanelImpl(IComponentImpl):

    def create_widget(self):
        raise NotImplementedError
    
    def initialize_widget(self):
        raise NotImplementedError

    def layout_child_widgets(self):
        raise NotImplementedError


class Panel(Component):
    """ The base panel wiget.

    Panel widgets hold a container of components and arrange them on an
    otherwise empty widget.

    Methods
    -------
    layout(parent)
        Initialize and layout the panel and it's children.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    _impl = Instance(IPanelImpl)

    children = List(Instance(Container))

    def layout(self):
        """ Initialize and layout the panel and it's children.

        Call this method after the object tree has been built in order
        to create and arrange the underlying widgets. It can be called 
        again at a later time in order to rebuild the view.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        impl = self._impl
        impl.create_widget()
        for container in self.children:
            container.layout()
        impl.initialize_widget()
        impl.layout_child_widgets()
        self._hook_impl()

