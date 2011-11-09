#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Event, Int, Str, Enum, Property, Instance, Any

from .text_editor import TextEditor, AbstractTkTextEditor


class AbstractTkCodeEditor(AbstractTkTextEditor):
    """ A text editor widget oriented toward code editing task.
    
    This is not a general text edit widget with general capabilties for sophistcated
    formatting or image display.
    """
    pass
    
class CodeEditor(TextEditor):
    """
    """
    
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkCodeEditor)
    
