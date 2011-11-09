#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from qt import QtGui

from pyface.ui.qt4.code_editor.code_widget import CodeWidget
from pyface.ui.qt4.code_editor.pygments_highlighter import PygmentsHighlighter

from .qt_text_editor import QtTextEditor

from ..code_editor import AbstractTkCodeEditor


class QtCodeEditor(QtTextEditor, AbstractTkCodeEditor):
    """ A Qt implementation of a code editor.

    QtCodeEditor uses the PyFace CodeWidget to provide a code editor widget.
    """

    #--------------------------------------------------------------------------
    # SetupMethods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying CodeWidget.

        """
        self.widget = CodeWidget(parent=self.parent_widget())

    def shell_highlight_current_line_changed(self):
        pass
    
    def shell_lexer_changed(self):
        pass
    
    def block_indent(self):
        """ Indent the selected lines of code.
        """
        self.widget.block_indent()
    
    def block_unindent(self):
        """ Unindent the selected lines of code.
        """
        self.widget.block_unindent()
    
    def block_comment(self):
        """ Unindent the selected lines of code.
        """
        self.widget.block_comment()

    def set_highlight_current_line(self, highlight_current_line):
        self.widget.should_highlight_current_line = highlight_current_line

    def set_lexer(self, lexer):
        """ Set the lexer used by the syntax highlighter
        """
        self.widget.highlighter = PygmentsHighlighter(self.widget.document(), lexer)