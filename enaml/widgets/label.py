#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Instance, Bool

from .control import Control, AbstractTkControl


class AbstractTkLabel(AbstractTkControl):
    
    @abstractmethod
    def shell_text_changed(self, text):
        raise NotImplementedError
        
    
    @abstractmethod
    def shell_word_wrap_changed(self, word_wrap):
        raise NotImplementedError


class Label(Control):
    """ A simple read-only text display.

    """
    #: The text in the label.
    text = Str
    
    #: Whether or not the label should wrap around on long lines.
    word_wrap = Bool(False)

    #: How strongly a component hugs it's content. Labels hug their
    #: contents' width weakly by default.
    hug_width = 'weak'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkLabel)

    # Note: Do not attempt to create a _text_changed handler here
    # to fire off size hint updated events. This is because such
    # a handler might get fired *before* the label is actually
    # updated and so the computed size hint will be incorrect.

