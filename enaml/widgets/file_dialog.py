#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Bool, Callable, List, Unicode

from enaml.core.declarative import Declarative
from enaml.core.trait_types import EnamlEvent


class FileDialog(Declarative):
    """ A dialog widget that allows the user to open and save files and
    directories.

    """
    #: The title to use for the dialog.
    title = Unicode

    #: The mode of the dialog.
    mode = Enum('open_file', 'open_files', 'save_file', 'directory')

    #: The selected path in the dialog. This value will be used to set
    #: the initial working directory and file, as appropriate, when the
    #: dialog is opened. It will aslo be updated when the dialog is
    #: closed and accepted.
    path = Unicode

    #: The list of selected paths in the dialog. It will be updated
    #: when the dialog is closed and accepted. It is output only and
    #: is only applicable for the `open_files` mode.
    paths = List(Unicode)

    #: The string filters used to restrict the user's selections.
    filters = List(Unicode)

    #: The selected filter from the list of filters. This value will be
    #: used as the initial working filter when the dialog is opened. It
    #: will also be updated when the dialog is closed and accepted.
    selected_filter = Unicode

    #: Whether to use a platform native dialog, when available.
    native_dialog = Bool(True)

    #: An enum indicating if the dialog was accepted or rejected by
    #: the user. It will be updated when the dialog is closed. This
    #: value is output only.
    result = Enum('rejected', 'accepted')

    #: An optional callback which will be invoked when the dialog is
    #: closed. This is a convenience to make it easier to handle the
    #: non-blocking behavior of the dialog. The callback must accept
    #: a single argument, which will be the dialog instance.
    callback = Callable

    #: An event fired when the dialog is closed. The dialog state will
    #: be updated before this event is fired.
    closed = EnamlEvent

    #: Whether to destroy the dialog widget on close. The default is
    #: True since dialogs are typically used in a transitory fashion.
    #: If this value is set to True, the dialog will be destroyed on
    #: the completion of the `closed` event.
    destroy_on_close = Bool(True)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the dialog for user interaction.

        """
        if self.parent is None:
            raise ValueError('FileDialog cannot be opened without a parent.')
        content = {}
        content['title'] = self.title
        content['mode'] = self.mode
        content['path'] = self.path
        content['filters'] = self.filters
        content['selected_filter'] = self.selected_filter
        content['native_dialog'] = self.native_dialog
        self.send_action('open', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.result = content['result']
        if self.result == 'accepted':
            paths = content['paths']
            self.paths = paths
            self.path = paths[0] if paths else u''
            self.selected_filter = content['selected_filter']
        if self.callback:
            self.callback(self)
        self.closed()
        if self.destroy_on_close:
            self.destroy()

