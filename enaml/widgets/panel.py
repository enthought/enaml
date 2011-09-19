#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, List

from .component import Component, IComponentImpl
from .container import Container


class IPanelImpl(IComponentImpl):
    pass


class Panel(Component):
    """ The base panel wiget.

    Panel widgets hold a container of components and arrange them on an
    otherwise empty widget.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IPanelImpl)

    children = List(Instance(Container))

