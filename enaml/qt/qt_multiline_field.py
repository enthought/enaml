#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QTextEdit
from .qt.QtCore import Signal, QTimer
from .qt_control import QtControl


class QMultilineEdit(QTextEdit):
    """ A QTextEdit which notifies on a collapsing timer.

    """
    delayedTextChanged = Signal()

    def __init__(self, parent=None):
        super(QMultilineEdit, self).__init__(parent)
        self._changed_timer = timer = QTimer()
        timer.setInterval(200)
        timer.setSingleShot(True)
        timer.timeout.connect(self.delayedTextChanged)
        self.textChanged.connect(timer.start)


class QtMultilineField(QtControl):
    """ A Qt4 implementation of an Enaml Field.

    """
    #: Whether or not to auto synchronize the text on change.
    _auto_sync_text = True

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QFocusMultiLineEdit widget.

        """
        return QMultilineEdit(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMultilineField, self).create(tree)
        self._auto_sync_text = tree['auto_sync_text']
        self.set_text(tree['text'])
        self.set_read_only(tree['read_only'])
        widget = self.widget()
        widget.delayedTextChanged.connect(self.on_text_changed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _send_text_changed(self):
        """ Send the current text as an update to the server widget.

        """
        text = self.widget().toPlainText()
        self.send_action('text_changed', {'text': text})

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_text_changed(self):
        """ The signal handler for 'delayedTextChanged' signal.

        """
        if self._auto_sync_text and 'text' not in self.loopback_guard:
            self._send_text_changed()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_auto_sync_text(self, content):
        """ Handle the 'set_auto_sync_text' action from the Enaml widget.

        """
        self._auto_sync_text = content['auto_sync_text']

    def on_action_set_read_only(self, content):
        """ Handle the 'set_read_only' action from the Enaml widget.

        """
        self.set_read_only(content['read_only'])

    def on_action_sync_text(self, content):
        """ Handle the 'sync_text' action from the Enaml widget.

        """
        self._send_text_changed()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        with self.loopback_guard('text'):
            self.widget().setText(text)

    def set_read_only(self, read_only):
        """ Set whether or not the widget is read only.

        """
        self.widget().setEnabled(not read_only)

