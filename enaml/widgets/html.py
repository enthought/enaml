#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Instance

from .control import Control, AbstractTkControl


class AbstractTkHtml(AbstractTkControl):
    
    @abstractmethod
    def shell_source_changed(self, source):
        raise NotImplementedError


class Html(Control):
    """ An extremely simple widget for displaying HTML.
    
    """
    #: The Html source code to be rendered.
    source = Str

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkHtml)

