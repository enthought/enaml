#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Unicode

from .control import Control


class MultilineField(Control):
    """ A simple multiline editable text widget.

    """
    #: The unicode text to display in the field.
    text = Unicode

    #: Whether or not the field is read only.
    read_only = Bool(False)

    #: Whether the text in the control should be auto-synchronized with
    #: the text attribute on the field. If this is True, the text will
    #: be updated every time the user edits the control. In order to be
    #: efficient, the toolkit will batch updates on a collapsing timer.
    auto_sync_text = Bool(True)

    #: Multiline fields expand freely in width and height by default.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the control.

        """
        snap = super(MultilineField, self).snapshot()
        snap['text'] = self.text
        snap['read_only'] = self.read_only
        snap['auto_sync_text'] = self.auto_sync_text
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(MultilineField, self).bind()
        self.publish_attributes('text', 'read_only', 'auto_sync_text')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_text_changed(self, content):
        """ Handle the 'text_changed' action from the client widget.

        """
        text = content['text']
        self.set_guarded(text=text)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def sync_text(self):
        """ Send a message to the toolkit to synchronize the text.

        """
        self.send_action('sync_text', {})

