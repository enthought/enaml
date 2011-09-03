from traits.api import Instance

from .component import Component, IComponentImpl


class IControlImpl(IComponentImpl):

    def create_widget(self):
        raise NotImplementedError
    
    def initialize_widget(self):
        raise NotImplementedError
    
    def layout_child_widgets(self):
        raise NotImplementedError


class Control(Component):
    """ The base class of all concretes widgets in TraitsML.

    Elements do not contain children and can be thought of 
    as terminal widgets in the TraitsML object tree.

    layout(parent)
        Initialize and layout the widget.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    _impl = Instance(IControlImpl)

    def layout(self):
        """ Initialize and layout the widget.

        This method should be called by the parent window during
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

