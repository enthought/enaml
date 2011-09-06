from traits.api import Instance

from .component import Component, IComponentImpl


class IControlImpl(IComponentImpl):
    pass


class Control(Component):
    """ The base class of all concrete widgets in Enaml.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IControlImpl)

