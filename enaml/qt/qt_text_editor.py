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
        self.set_columns(len(self.attrs['documents']))
        self.widget.loadFinished.connect(self.on_load)

    def on_load(self):
        """ The attributes have to be set after the webview
        has finished loading, so this function is delayed

        """
        self.set_documents(self.attrs['documents'])
        self.set_theme(self.attrs['theme'])
        self.set_auto_pair(self.attrs['auto_pair'])
        self.set_font_size(self.attrs['font_size'])
        self.set_margin_line(self.attrs['margin_line'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_documents(self, payload):
        """ Handle the 'set-documents' action from the Enaml widget.

        """
        self.set_documents(payload['documents'])

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

    def on_message_set_text(self, payload):
        """ Handle the 'set-text' action from the Enaml widget.

        """
        self.set_text(payload['col_index'], payload['tab_index'],
            payload['text'])

    def on_message_set_title(self, payload):
        """ Handle the 'set-title' action from the Enaml widget.

        """
        self.set_title(payload['col_index'], payload['tab_index'],
            payload['title'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_columns(self, columns):
        """ Set the number of columns in the editor.

        """
        self.widget.set_columns(columns)

    def set_documents(self, documents):
        """ Set the document in the underlying widget.

        """
        for column in documents:
            for document in column:
                col = documents.index(column)
                i = column.index(document)
                self.set_text(col, i, document['text'])
                self.set_mode(col, i, document['mode'])
                self.set_title(col, i, document['title'])

    def set_text(self, col_index, tab_index, text):
        """ Set the text of a document

        """
        self.widget.editor().set_text(col_index, tab_index, text)

    def set_mode(self, col_index, tab_index, mode):
        """ Set the mode of a document

        """
        self.widget.editor().set_mode(col_index, tab_index, mode)

    def set_title(self, col_index, tab_index, title):
        """ Set the title of a document

        """
        self.widget.editor().set_title(col_index, tab_index, title)

    def set_auto_pair(self, auto_pair):
        """ Set whether or not to auto pair in a document

        """
        self.widget.editor().set_auto_pair(auto_pair)

    def set_font_size(self, font_size):
        """ Set the font size of a document

        """
        self.widget.editor().set_font_size(font_size)

    def set_margin_line(self, margin_line):
        """ Set the margin line of a document

        """
        self.widget.editor().set_margin_line(margin_line)

    def set_theme(self, theme):
        """ Set the theme of the editor

        """
        self.widget.editor().set_theme(theme)
