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
        self.set_columns(attrs['columns'])
        self.widget.loadFinished.connect(self.on_load)

    def on_load(self):
        """ The attributes have to be set after the webview
        has finished loading, so this function is delayed

        """
        self.set_documents(self.attrs['documents'])
        self.set_theme(self.attrs['theme'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_columns(self, payload):
        """ Handle the 'set-columns' action from the Enaml widget.

        """
        self.set_columns(payload['columns'])

    def on_message_set_documents(self, payload):
        """ Handle the 'set-documents' action from the Enaml widget.

        """
        self.set_documents(payload['documents'])

    def on_message_set_theme(self, payload):
        """ Handle the 'set-theme' action from the Enaml widget.

        """
        self.set_theme(payload['theme'])

    def on_message_set_text(self, payload):
        """ Handle the 'set-text' action from the Enaml widget.

        """
        self.set_text(payload['index'], payload['text'])

    def on_message_set_title(self, payload):
        """ Handle the 'set-title' action from the Enaml widget.

        """
        self.set_title(payload['index'], payload['title'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_columns(self, columns):
        """ Set the number of columns in the editor.

        """
        self.widget.set_columns(columns)
        self._columns = columns

    def set_documents(self, documents):
        """ Set the document in the underlying widget.

        """
        for i in range(min(len(documents), self._columns)):
            self.set_text(i, documents[i]['text'])
            self.set_mode(i, documents[i]['mode'])
            self.set_title(i, documents[i]['title'])
            self.set_auto_pair(i, documents[i]['auto_pair'])
            self.set_font_size(i, documents[i]['font_size'])
            self.set_margin_line(i, documents[i]['margin_line'])

    def set_text(self, index, text):
        """ Set the text of the document at index

        """
        self.widget.editor().set_text(index, text)

    def set_mode(self, index, mode):
        """ Set the mode of the document at index

        """
        self.widget.editor().set_mode(index, mode)

    def set_title(self, index, title):
        """ Set the title of the document at index

        """
        self.widget.editor().set_title(index, title)

    def set_auto_pair(self, index, auto_pair):
        """ Set whether or not to auto pair in the document at index

        """
        self.widget.editor().set_auto_pair(index, auto_pair)

    def set_font_size(self, index, font_size):
        """ Set the font size of the document at index

        """
        self.widget.editor().set_font_size(index, font_size)

    def set_margin_line(self, index, margin_line):
        """ Set the margin line of the document at index

        """
        self.widget.editor().set_margin_line(index, margin_line)

    def set_theme(self, theme):
        """ Set the theme of the editor

        """
        self.widget.editor().set_theme(theme)
