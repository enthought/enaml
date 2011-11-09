#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from qt import QtGui

from pyface.ui.qt4.code_editor.code_widget import CodeWidget
from pyface.ui.qt4.code_editor.pygments_highlighter import PygmentsHighlighter

from .qt_text_editor import QtTextEditor
from .styling import q_color_from_color, q_font_from_font

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
    
    def initialize(self):
        """ Initializes the attributes of the Qt widget.

        """
        super(QtCodeEditor, self).initialize()
        shell = self.shell_obj
        self.set_language(shell.language)


    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    
    def shell_language_changed(self):
        self.set_language(self.shell_obj.language)
    
    def block_indent(self):
        """ Indent the selected lines of code.
        """
        print 'calling indent'
        self.widget.block_indent()
    
    def block_unindent(self):
        """ Unindent the selected lines of code.
        """
        self.widget.block_unindent()
    
    def block_comment(self):
        """ Unindent the selected lines of code.
        """
        self.widget.block_comment()

    #--------------------------------------------------------------------------
    # Internal methods
    #--------------------------------------------------------------------------
        

    def set_language(self, language):
        """ Set the language lexer used by the syntax highlighter
        
        This uses Pygments under the covers so language names are converted to
        Pygments lexers.
        """
        old_highlighter = self.widget.highlighter
        self.widget.highlighter = PygmentsHighlighter(self.widget.document(), language)
    
    def set_font(self, font):
        """ Set the font of the underlying toolkit widget to an appropriate
        QFont.
        
        We override default behaviour so we can change the size hint and gutter.
        """
        q_font = q_font_from_font(font)
        self.widget.set_font(q_font)