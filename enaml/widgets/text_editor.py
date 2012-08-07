#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Int, Instance, List
from ..noncomponents.document import Document
from .constraints_widget import ConstraintsWidget


class TextEditor(ConstraintsWidget):
    """ A control for editing text, geared toward code.

    """
    #: The number of columns of editors to display
    columns = Int(1)

    #: A list of documents to be displayed
    documents = List(Instance(Document))

    #: The theme for the document
    theme = Unicode("textmate")

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Returns the dict of creation attributes for the control.

        """
        super_attrs = super(TextEditor, self).creation_attributes()
        super_attrs['columns'] = self.columns
        super_attrs['documents'] = [doc.as_dict() for doc in self.documents]
        super_attrs['theme'] = self.theme
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TextEditor, self).bind()
        self.publish_attributes('columns', 'documents', 'theme')

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def set_text(self, text, index=0):
        """ Set the text of the document at index

        """
        self.send_message({
            'action': 'set-text',
            'index': index,
            'text': text
        })

    def set_title(self, title, index=0):
        """ Set the title of the document at index

        """
        self.send_message({
            'action': 'set-title',
            'index': index,
            'title': title
        })
