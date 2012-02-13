#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Tuple, Int

from .control import Control, IControlImpl


class ISpacerImpl(IControlImpl):
    
    def parent_size_changed(self):
        raise NotImplementedError


class Spacer(Control):
    
    size = Tuple((-1, -1))

    toolkit_impl = Instance(ISpacerImpl)

