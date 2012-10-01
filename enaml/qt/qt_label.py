#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QLabel
from .qt_constraints_widget import QtConstraintsWidget


class QtLabel(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Label.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying label widget.

        """
        return QLabel(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtLabel, self).create(tree)
        self.set_text(tree['text'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        item = self.widget_item()
        old_hint = item.sizeHint()
        self.set_text(content['text'])
        new_hint = item.sizeHint()
        if old_hint != new_hint:
            self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget().setText(text)

