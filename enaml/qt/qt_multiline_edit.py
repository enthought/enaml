#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .qt.QtGui import QTextEdit
from .qt.QtCore import Signal, QTimer
from .qt_control import QtControl


class QtFocusMultiLineEdit(QTextEdit):
    """ A QLineEdit subclass which converts a lost focus event into
    a lost focus signal.

    """
    lostFocus = Signal()
    delayedTextChanged = Signal()

    def __init__(self, parent=None):
        super(QtFocusMultiLineEdit, self).__init__(parent)

        # Set up a collapsing timer to fire 200 milliseconds
        # after the text is changed
        self._changed_timer = timer = QTimer()
        timer.setInterval(200)
        timer.setSingleShot(True)
        timer.timeout.connect(self.delayedTextChanged.emit)

        # Connect the timer to the text changed signal
        self.textChanged.connect(timer.start)

    def focusOutEvent(self, event):
        self.lostFocus.emit()
        return super(QtFocusMultiLineEdit, self).focusOutEvent(event)


class QtMultiLineEdit(QtControl):
    """ A Qt4 implementation of an Enaml Field.

    """
    #: The list of submit triggers for when to submit a text change.
    _submit_triggers = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QLineEdit widget.

        """
        return QtFocusMultiLineEdit(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMultiLineEdit, self).create(tree)
        self.set_text(tree['text'])
        self.set_submit_triggers(tree['submit_triggers'])
        self.set_read_only(tree['read_only'])
        widget = self.widget()
        widget.lostFocus.connect(self.on_lost_focus)
        widget.delayedTextChanged.connect(self.on_text_changed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _submit_text(self):
        """ Submit the given text as an update to the server widget.

        Parameters
        ----------
        text : unicode
            The unicode text to send to the server widget.

        """
        text = self.widget().toPlainText()
        content = {'text': text}
        self.send_action('submit_text', content)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_lost_focus(self):
        """ The signal handler for 'lostFocus' signal.

        """
        if 'lost_focus' in self._submit_triggers:
            self._submit_text()

    def on_text_changed(self):
        """ The signal handler for 'delayedTextChanged' signal.

        """
        if 'text_changed' in self._submit_triggers:
            self._submit_text()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_submit_triggers(self, content):
        """ Handle the 'set_submit_triggers' action from the Enaml
        widget.

        """
        self.set_submit_triggers(content['submit_triggers'])

    def on_action_set_read_only(self, content):
        """ Handle the 'set_read_only' action from the Enaml widget.

        """
        self.set_read_only(content['read_only'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget().setText(text)

    def set_submit_triggers(self, triggers):
        """ Set the submit triggers for the underlying widget.

        """
        self._submit_triggers = triggers

    def set_read_only(self, read_only):
        """ Set whether or not the widget is read only.

        """
        self.widget().setEnabled(not read_only)

