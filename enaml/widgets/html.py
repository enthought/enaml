#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, Instance

from .control import Control, IControlImpl


class IHtmlImpl(IControlImpl):
    
    def parent_source_changed(self, source):
        raise NotImplementedError


class Html(Control):
    """ A simple widget for displaying HTML.
    
    Attributes
    ----------
    source : Str
        The Html source code to be rendered.
    
    """
    source = Str

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    tookit_impl = Instance(IHtmlImpl)

