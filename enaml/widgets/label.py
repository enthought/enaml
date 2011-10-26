#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Instance

from .control import Control, AbstractTkControl


class AbstractTkLabel(AbstractTkControl):
    
    @abstractmethod
    def shell_text_changed(self, text):
        raise NotImplementedError
        
    
class Label(Control):
    """ A simple read-only text display.

    """
    #: The text in the label.
    text = Str

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkLabel)

