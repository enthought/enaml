#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Int, List, Bool
from .constraints_widget import ConstraintsWidget


class TextEditor(ConstraintsWidget):
    """ A control for editing text, geared toward code.

    """
    #: A nested list of documents to be displayed. The outer list represents
    #: columns and the inner lists represent tabs within the column.
    documents = List

    #: The theme for the document
    theme = Unicode("textmate")

    #: Auto pairs parentheses, braces, etc
    auto_pair = Bool(True)

    #: The editor's font size
    font_size = Int(12)

    #: Display the margin line at a certain column. A value of -1 hides the
    #: margin line.
    margin_line = Int(-1)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Returns the dict of creation attributes for the control.

        """
        for column in self.documents:
            for doc in column:
                doc.col = self.documents.index(column)
                doc.tab = column.index(doc)
                doc.on_trait_change(self.title_changed, 'title')
                doc.on_trait_change(self.text_changed, 'text')
                doc.on_trait_change(self.mode_changed, 'mode')

        super_attrs = super(TextEditor, self).creation_attributes()
        super_attrs['documents'] = [[doc.as_dict() for doc in col]
                                        for col in self.documents]
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
        self.publish_attributes('columns', 'theme', 'auto_pair', 'font_size',
            'margin_line', 'documents[]')

    def title_changed(self, _object, name, new):
        payload = {
            'action': 'set-title',
            'col_index': _object.col,
            'tab_index': _object.tab,
            'title': new
        }
        self.send_message(payload)

    def text_changed(self, _object, name, new):
        payload = {
            'action': 'set-text',
            'col_index': _object.col,
            'tab_index': _object.tab,
            'text': new
        }
        self.send_message(payload)

    def mode_changed(self, _object, name, new):
        payload = {
            'action': 'set-mode',
            'col_index': _object.col,
            'tab_index': _object.tab,
            'mode': new
        }
        self.send_message(payload)
