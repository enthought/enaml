#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance
from enable.component import Component as EnableComponent

from .control import Control, IControlImpl


class IEnableCanvasImpl(IControlImpl):

    def parent_component_changed(self, component):
        raise NotImplementedError


class EnableCanvas(Control):
    """ An Enable widget.
    
    """
    # An enable component
    component = Instance(EnableComponent)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IEnableCanvasImpl)

