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
        self.widget.loadFinished.connect(self.set_attrs)
        
    def set_attrs(self):
        """ The attributes have to be set after the webview
        has finished loading, so this function is delayed

        """
        self.set_text(self.attrs['text'])
        self.set_theme(self.attrs['theme'])
        self.set_mode(self.attrs['mode'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_text(self, payload):
        """ Handle the 'set-text' action from the Enaml widget.

        """
        self.set_text(payload['text'])

    def on_message_set_theme(self, payload):
        """ Handle the 'set-theme' action from the Enaml widget.

        """
        self.set_theme(payload['theme'])

    def on_message_set_mode(self, payload):
        """ Handle the 'set-mode' action from the Enaml widget.

        """
        self.set_mode(payload['mode'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget.editor().set_text(text)

    def set_theme(self, theme):
        """ Set the theme of the underlying editor.

        """
        self.widget.editor().set_theme(theme)

    def set_mode(self, mode):
        """ Set the mode of the underlying editor.

        """
        self.widget.editor().set_mode(mode)
