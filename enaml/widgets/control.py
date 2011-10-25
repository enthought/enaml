#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance

from .component import Component, AbstractTkComponent

from .layout_item import LayoutItem, AbstractTkLayoutItem


class AbstractTkControl(AbstractTkComponent, AbstractTkLayoutItem):
    pass


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

    #--------------------------------------------------------------------------
    # Overridden parent class traits
    #--------------------------------------------------------------------------
    abstract_widget = Instance(AbstractTkControl)

    def relayout(self):
        self.parent.relayout()
    
    def reconstrain(self):
        self.parent.reconstrain()

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def _constraints_changed(self):
        # 'constraints' is an attribute on LayoutItem. When a new list 
        # of constraints is applied, we need to ask our parent (a Container)
        # to reconstrain everything
        self.reconstrain()
        self.relayout()

