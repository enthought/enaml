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
        self.widget.ace_editor.text_changed_from_js.connect(self.on_text_change)
        self.widget.ace_editor.tab_added.connect(self.on_tab_added)
        self.widget.ace_editor.tab_removed.connect(self.on_tab_removed)

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
        self.set_tabs(self.attrs['tabs'])

    #--------------------------------------------------------------------------
    # Event handlers
    #--------------------------------------------------------------------------
    def on_text_change(self, col_index, tab_index, text):
        """ Event fired when the editor text is changed.

        """
        payload = {
            'action': 'event-text-changed',
            'col_index': col_index,
            'tab_index': tab_index,
            'text': text
        }
        self.send_message(payload)

    def on_tab_added(self, col_index, tab_index):
        """ Event fired when a tab is added to the editor

        """
        payload = {
            'action': 'event-tab-added',
            'col_index': col_index,
            'tab_index': tab_index
        }
        self.send_message(payload)

    def on_tab_removed(self, col_index, tab_index):
        """ Event fired when a tab is removed from the editor

        """
        payload = {
            'action': 'event-tab-removed',
            'col_index': col_index,
            'tab_index': tab_index
        }
        self.send_message(payload)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_tabs(self, payload):
        """ Handle the 'set-tabs' action from the Enaml widget.

        """
        self.set_tabs(payload['tabs'])

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

    def on_message_set_mode(self, payload):
        """ Handle the 'set-mode' action from the Enaml widget.

        """
        self.set_mode(payload['col_index'], payload['tab_index'],
            payload['mode'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_tabs(self, tabs):
        """ Set whether or not to show tabs

        """
        self.widget.editor().set_tabs(tabs)

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
