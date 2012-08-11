#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Int, List, Bool
from .constraints_widget import ConstraintsWidget
from ..noncomponents.document import Document


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

    #: Whether or not to show tabs
    tabs = Bool(False)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        for column in self.documents:
            for doc in column:
                doc.col = self.documents.index(column)
                doc.tab = column.index(doc)
                doc.on_trait_change(self.title_changed, 'title')
                doc.on_trait_change(self.text_changed, 'text')
                doc.on_trait_change(self.mode_changed, 'mode')

        snap = super(TextEditor, self).snapshot()
        snap['documents'] = [[doc.as_dict() for doc in col]
                                        for col in self.documents]
        snap['theme'] = self.theme
        snap['auto_pair'] = self.auto_pair
        snap['font_size'] = self.font_size
        snap['margin_line'] = self.margin_line
        snap['tabs'] = self.tabs

        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TextEditor, self).bind()
        self.publish_attributes('theme', 'auto_pair', 'font_size', 'tabs',
            'margin_line')
        self.on_trait_change(self.documents_changed, 'documents')

    #--------------------------------------------------------------------------
    # Action Handlers
    #--------------------------------------------------------------------------
    def on_action_text_changed(self, content):
        """ Update the text of a document.


        """
        # XXX This should probably be done with loopback guards, but I could
        # not get it working. We need a better solution than unhooking and
        # reattaching the trait change listener.
        col_index = content['col_index']
        tab_index = content['tab_index']
        text = content['text']
        doc = self.documents[col_index][tab_index]
        doc.on_trait_change(self.text_changed, 'text', remove=True)
        doc.text = text
        doc.on_trait_change(self.text_changed, 'text')

    def on_action_tab_added(self, content):
        """ Update the documents list to reflect the added tab

        """
        col_index = content['col_index']
        tab_index = content['tab_index']
        self.documents[col_index].insert(tab_index, Document())

    def on_action_tab_removed(self, content):
        """ Update the documents list to reflect the removed tab

        """
        col_index = content['col_index']
        tab_index = content['tab_index']
        del self.documents[col_index][tab_index]

    def on_action_tab_moved(self, content):
        """ Update the documents list to reflect the moved tab

        """
        old_col = content['old_col']
        old_tab = content['old_tab']
        new_col = content['new_col']
        new_tab = content['new_tab']
        doc = self.documents[old_col].pop(old_tab)
        self.documents[new_col].insert(new_tab, doc)

    #--------------------------------------------------------------------------
    # Trait Change Handlers
    #--------------------------------------------------------------------------
    def documents_changed(self, new):
        """ Fired when the documents are changed.

        """
        content = {
            'documents': [[doc.as_dict() for doc in col] for col in new]
        }
        self.send_action('set_documents', content)

    def title_changed(self, _object, name, new):
        """ Fired when the title trait changes on a document

        """
        content = {
            'col_index': _object.col,
            'tab_index': _object.tab,
            'title': new
        }
        self.send_action('set_title', content)

    def text_changed(self, _object, name, new):
        """ Fired when the text trait changes on a document

        """
        content = {
            'col_index': _object.col,
            'tab_index': _object.tab,
            'text': new
        }
        self.send_action('set_text', content)

    def mode_changed(self, _object, name, new):
        """ Fired when the mode trait changes on a document

        """
        content = {
            'col_index': _object.col,
            'tab_index': _object.tab,
            'mode': new
        }
        self.send_action('set_mode', content)
