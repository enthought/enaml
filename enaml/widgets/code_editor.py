#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Event, Int, Str, Enum, Property, Instance, Any

from .text_editor import TextEditor, AbstractTkTextEditor


class AbstractTkCodeEditor(AbstractTkTextEditor):
    """ A text editor widget oriented toward code editing.
    
    This is not a general text edit widget with general capabilties for sophistcated
    formatting or image display.
    """

    @abstractmethod
    def shell_language_changed(self):
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
    
    @abstractmethod
    def block_comment(self):
        """ Comment out or uncomment the selected lines of code.
        """
        pass

class CodeEditor(TextEditor):
    """ A text editor widget oriented toward code editing.

    This is not a general text edit widget with general capabilties for
    sophistcated formatting or image display.
    """
    
    #: The language to use for syntax highlighting
    language = Str
    
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkCodeEditor)
    
    def block_indent(self):
        """ Indent the selected lines of code.
        """
        self.abstract_obj.block_indent()
    
    def block_unindent(self):
        """ Unindent the selected lines of code.
        """
        self.abstract_obj.block_unindent()
    
    def block_comment(self):
        """ Comment or uncomment the selected lines of code.
        """
        self.abstract_obj.block_comment()
