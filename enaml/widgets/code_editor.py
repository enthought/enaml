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
    @abstractmethod
    def shell_highlight_current_line_changed(self):
        pass
    
    @abstractmethod
    def shell_lexer_changed(self):
        pass
    
    @abstractmethod
    def block_indent(self):
        """ Indent the selected lines of code.
        """
        pass
    
    @abstractmethod
    def block_unindent(self):
        """ Unindent the selected lines of code.
        """
        pass

class CodeEditor(TextEditor):
    """
    """
    
    #: Whether or not we should highlight the current line
    highlight_current_line = Bool
    
    #: The lexer to use for syntax highlighting
    lexer = Any
    
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkCodeEditor)
    
