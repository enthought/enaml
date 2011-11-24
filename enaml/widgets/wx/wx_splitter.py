#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
import wx
from wx.lib.splitter import MultiSplitterWindow

from .wx_container import WXContainer

from ..splitter import AbstractTkSplitter


_ORIENTATION_MAP = {
    'horizontal': wx.HORIZONTAL,
    'vertical': wx.VERTICAL,
}


class WXSplitter(WXContainer, AbstractTkSplitter):
    """ Wx implementation of the Splitter Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QSplitter control.

        """
        style = wx.SP_LIVE_UPDATE
        self.widget = MultiSplitterWindow(self.parent_widget(), style=style)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXSplitter, self).initialize()
        self.set_orientation(self.shell_obj.orientation)
        self.update_children()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_orientation_changed(self, orientation):
        """ Update the orientation of the widget.

        """
        self.set_orientation(orientation)

    def shell_children_changed(self, children):
        """ Update the widget with new children.

        """
        self.update_children()

    def shell_children_items_changed(self, event):
        """ Update the widget with new children.

        """
        self.update_children()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Update the orientation of the QSplitter.

        """
        wx_orientation = _ORIENTATION_MAP[orientation]
        self.widget.SetOrientation(wx_orientation)

    def update_children(self):
        """ Update the QSplitter's children with the current 
        children.

        """
        shell = self.shell_obj
        widget = self.widget
        # XXX using private _windows attribute. Is there no way
        # to query the splitter for it's windows?
        for widget_child in widget._windows:
            widget.DetachWindow(widget_child)

        for child in shell.children:
            child_widget = child.toolkit_widget
            child_widget.Reparent(widget)
            widget.AppendWindow(child_widget)

    def size_hint(self):
        """ Return a size hint for the widget.

        """
        return (296, 172)
        # along_hint = 0
        # ortho_hint = 0
        # shell = self.shell_obj
        # i = ['horizontal', 'vertical'].index(shell.orientation)
        # j = 1 - i
        # for child in shell.children:
        #     if child.visible:
        #         size_hint = child.size_hint()
        #         if size_hint == (-1, -1):
        #             min_size = child.toolkit_widget.minimumSize()
        #             size_hint = (min_size.width(), min_size.height())
        #         # FIXME: Add handle widths? QSplitter doesn't.
        #         along_hint += size_hint[i]
        #         ortho_hint = max(ortho_hint, size_hint[j])
        # if shell.orientation == 'horizontal':
        #     return (along_hint, ortho_hint)
        # else:
        #     return (ortho_hint, along_hint)

    def set_initial_sizes(self):
        """ Set the initial sizes for the children.

        """
        return
        # shell = self.shell_obj
        # i = ['horizontal', 'vertical'].index(shell.orientation)
        # sizes = []
        # for child in shell.children:
        #     hint = child.size_hint()[i]
        #     if hint <= 0:
        #         min_size = child.toolkit_widget.minimumSize()
        #         hint = (min_size.width(), min_size.height())[i]
        #     sizes.append(hint)
        # self.widget.setSizes(sizes)

