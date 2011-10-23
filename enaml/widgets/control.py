#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance

from .component import Component, IComponentImpl

from ..layout.layout_item import LayoutItem


class IControlImpl(IComponentImpl):
    
    def size(self):
        raise NotImplementedError

    def position(self):
        raise NotImplementedError

    def geometry(self):
        raise NotImplementedError
    
    def set_size(self, size):
        raise NotImplementedError

    def set_position(self, position):
        raise NotImplementedError

    def set_geometry(self, x, y, width, height):
        raise NotImplementedError

    def preferred_size(self):
        raise NotImplementedError
    
    def set_preferred_size(self):
        raise NotImplementedError


class Control(Component, LayoutItem):
    """ The base class of all concrete widgets in Enaml.

    Attributes
    ----------

    error : Bool
        A read only property which indicates whether an exception was raised
        through user interaction or setting a value trait on the Control.
    
    exception : Instance(Exception)
        A read only property which holds the exceptions raised if we are in an
        error state.

    """
    error = Bool

    exception = Instance(Exception)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IControlImpl)

    def initialize_layout(self):
        pass

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def _constraints_changed(self):
        self.parent.reconstrain()
        self.parent.relayout()


Control.protect('error', 'exception')

