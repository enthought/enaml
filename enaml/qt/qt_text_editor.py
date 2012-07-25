#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .editor.qt_ace_editor_view import QtAceEditorView
from .qt_constraints_widget import QtConstraintsWidget


class QtTextEditor(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml TextEditor.

    """
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = QtAceEditorView(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtTextEditor, self).initialize(attrs)
        self.attrs = attrs
        self.widget.loadFinished.connect(self.on_load)
        self.widget.ace_editor.document_changed.connect(self.on_document_changed)

    def on_load(self):
        """ The attributes have to be set after the webview
        has finished loading, so this function is delayed

        """
        self.set_document(self.attrs['document'])
        self.set_theme(self.attrs['theme'])
        self.set_auto_pair(self.attrs['auto_pair'])
        self.set_font_size(self.attrs['font_size'])
        self.set_margin_line(self.attrs['margin_line'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_document(self, payload):
        """ Handle the 'set-document' action from the Enaml widget.

        """
        self.set_document(payload['document'])

    def on_message_set_theme(self, payload):
        """ Handle the 'set-theme' action from the Enaml widget.

        """
        self.set_theme(payload['theme'])

    def on_message_set_auto_pair(self, payload):
        """ Handle the 'set-auto_pair' action from the Enaml widget.

        """
        self.set_auto_pair(payload['auto_pair'])

    def on_message_set_font_size(self, payload):
        """ Handle the 'set-font_size' action from the Enaml widget.

        """
        self.set_font_size(payload['font_size'])

    def on_message_set_margin_line(self, payload):
        """ Handle the 'set-margin_line' action from the Enaml widget.

        """
        self.set_margin_line(payload['margin_line'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_document(self, document):
        """ Set the document in the underlying widget.

        """
        self._document = document
        self.widget.editor().set_text(document.text)
        self.widget.editor().set_mode(document.mode)

    def set_theme(self, theme):
        """ Set the theme of the editor

        """
        self.widget.editor().set_theme(theme)

    def set_auto_pair(self, auto_pair):
        """ Set whether or not to pair parentheses, braces, etc in the editor

        """
        self.widget.editor().set_auto_pair(auto_pair)

    def set_font_size(self, font_size):
        """ Set the font size of the editor

        """
        self.widget.editor().set_font_size(font_size)

    def set_margin_line(self, margin_line):
        """ Set whether or not to display the margin line in the editor

        """
        if type(margin_line) == bool:
            self.widget.editor().show_margin_line(margin_line)
        else:
            self.widget.editor().set_margin_line_column(margin_line)
            self.widget.editor().show_margin_line(True)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_document_changed(self, text):
        """ Signal handler for the 'document_changed' signal.

        """
        self._document.text = text
        payload = {
            'action': 'set-document',
            'document': self._document
        }
        self.send_message(payload)
