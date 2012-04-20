#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os
import re

import wx

from .wx_dialog import WXDialog

from ...components.file_dialog import AbstractTkFileDialog
from ...guard import guard


STYLE_MODE_MAP = {
    'open': wx.FD_OPEN,
    'save': wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
}


FILTER_RE = re.compile(r'\((.*?\*.*?)\)')


class WXFileDialog(WXDialog, AbstractTkFileDialog):
    """ A Wx implementation of a FileDialog.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.FileDialog control.

        """
        self.widget = wx.FileDialog(parent)

    def initialize(self):
        """ Initializes the attributes of the underlying QFileDialog.

        """
        super(WXFileDialog, self).initialize()
        shell = self.shell_obj
        self.set_mode(shell.mode)
        self.set_multi_select(shell.multi_select)
        self.set_directory(shell.directory)
        self.set_filename(shell.filename)
        self.set_filters(shell.filters)
        self.set_selected_filter(shell.selected_filter)
    
    # The wx.FileDialog doesn't emit events for anything useful, 
    # so there is nothing which need be bound.

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_mode_changed(self, mode):
        """ Update the dialog for the given mode of behavior.

        """
        self.set_mode(mode)

    def shell_multi_select_changed(self, multi_select):
        """ Update the dialog for the given multi select behavior.

        """
        self.set_multi_select(multi_select)

    def shell_directory_changed(self, directory):
        """ Update the dialog with the new working directory.

        """
        if not guard.guarded(self, 'setting_directory'):
            self.set_directory(directory)
                
    def shell_filename_changed(self, filename):
        """ Update the dialog with the new selected filename.

        """
        if not guard.guarded(self, 'setting_filename'):
            self.set_filename(filename)

    def shell_filters_changed(self, filters):
        """ Update the dialog with the new filename filters.

        """
        # Traits doens't fire off a change event if an Enum updates
        # because its underlying values have changed. So, we just 
        # set the selected filter manually here to cover that case.
        self.set_filters(filters)
        self.set_selected_filter(self.shell_obj.selected_filter)

    def shell_selected_filter_changed(self, selected_filter):
        """ Update the dialog with the new selected filter.

        """
        if not guard.guarded(self, 'setting_selected_filter'):
            self.set_selected_filter(selected_filter)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_mode(self, mode):
        """ Sets the mode behavior of the file dialog.

        """
        self.widget.SetWindowStyle(STYLE_MODE_MAP[mode])
    
    def set_multi_select(self, multi_select):
        """ Sets the multi select behavior of the file dialog.

        """
        widget = self.widget
        style = widget.GetWindowStyle()
        if style & wx.FD_OPEN:
            if multi_select:
                style |= wx.FD_MULTIPLE
            else:
                style &= ~wx.FD_MULTIPLE
            widget.SetWindowStyle(style)

    def set_directory(self, directory):
        """ Sets the current directory of the dialog.

        """
        self.widget.SetDirectory(directory)
    
    def set_filename(self, filename):
        """ Sets the selected filename in the dialog.

        """
        self.widget.SetFilename(filename)
    
    def set_filters(self, filters):
        """ Sets the name filters in the file dialog.

        """
        # This converts Qt's filter format, which is used by the shell
        # object, into wx's wildcard format.
        parts = []
        for filt in filters:
            parts.append(filt)
            match = FILTER_RE.search(filt)
            if match:
                filt = match.group(1)
            parts.append(u';'.join(filt.split()))
        wildcard = u'|'.join(parts)
        self.widget.SetWildcard(wildcard)
    
    def set_selected_filter(self, selected_filter):
        """ Sets the selected name filter in the file dialog.

        """
        try:
            idx = self.shell_obj.filters.index(selected_filter)
        except ValueError:
            return
        self.widget.SetFilterIndex(idx)

    def set_central_widget(self, widget):
        """ Overridden parent class method which makes central widget
        operations a no-op, since a file dialog has no children.

        """
        pass

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def _handle_retcode(self, retcode):
        """ Overridden parent class method to update the shell object
        with new info once the dialog is closed.

        """
        widget = self.widget
        shell = self.shell_obj
        if retcode == wx.ID_OK:
            paths = widget.GetPaths()
            first_path = paths[0] if paths else u''
            with guard(self, 'setting_directory'):
                with guard(self, 'setting_filename'):
                    shell.directory, shell.filename = os.path.split(first_path)
                    shell._paths = paths
        idx = widget.GetFilterIndex()
        if idx < len(shell.filters):
            shell.selected_filter = shell.filters[idx]
        super(WXFileDialog, self)._handle_retcode(retcode)

