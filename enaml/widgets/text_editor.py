#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Bool, Int, Instance, Either
from ..noncomponents.document import Document
from .constraints_widget import ConstraintsWidget


class TextEditor(ConstraintsWidget):
    """ A simple control for displaying read-only text.

    """
    #: The document that is currently displayed
    document = Instance(Document, ())

    #: The theme for the document
    theme = Unicode("textmate")

    #: Auto pairs parentheses, braces, etc
    auto_pair = Bool(True)

    #: The editor's font size
    font_size = Int(12)

    #: Display the margin line at a certain column
    margin_line = Either(Bool(True), Int(80))

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Returns the dict of creation attributes for the control.

        """
        super_attrs = super(TextEditor, self).creation_attributes()
        super_attrs['document'] = self.document
        super_attrs['theme'] = self.theme
        super_attrs['auto_pair'] = self.auto_pair
        super_attrs['font_size'] = self.font_size
        super_attrs['margin_line'] = self.margin_line
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TextEditor, self).bind()
        self.publish_attributes('document', 'theme', 'auto_pair', 'font_size',
            'margin_line')

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_document(self, payload):
        """ Message handler for the 'set-document' action

        XXX Confusing as this handler does not correspond to the
        set_document method below

        """
        self.document = payload['document']

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def set_document(self, document):
        """ Set the current document of the text editor

        """
        payload = {
            'action': 'set-document',
            'document': document
        }
        self.send_message(payload)
