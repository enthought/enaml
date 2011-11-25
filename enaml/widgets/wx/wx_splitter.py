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


class CustomSplitter(MultiSplitterWindow):
    """ A wx.lib.splitter.MultiSplitterWindow subclass that changes
    the behavior of resizing neighbors to be consisten with Qt.

    """
    def _OnMouse(self, event):
        """ Overriden parent class mouse event handler which fakes the
        state of the keyboard so that resize behavior is consistent
        between wx and Qt.

        """
        # We modify the mouse event to "fake" like the shift key is
        # always down. This causes the splitter to not adjust its 
        # neighbor when dragging the sash. This behavior is consistent
        # with Qt's behavior. This is not *the best* way to handle this,
        # but it's the easiest and quickest at the moment. The proper 
        # way would be to reimplement this method in its entirety and
        # allow the adjustNeighbor computation to be based on keyboard
        # state as well as attribute flags. 
        #
        # TODO implement this properly
        event.m_shiftDown = True
        return super(CustomSplitter, self)._OnMouse(event)


class WXSplitter(WXContainer, AbstractTkSplitter):
    """ Wx implementation of the Splitter Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QSplitter control.

        """
        self.widget = CustomSplitter(self.parent_widget())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXSplitter, self).initialize()
        shell = self.shell_obj
        self.set_orientation(shell.orientation)
        self.set_live_drag(shell.live_drag)
        self.update_children()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_orientation_changed(self, orientation):
        """ Update the orientation of the widget.

        """
        self.set_orientation(orientation)

    def shell_live_drag_changed(self, live_drag):
        """ The change handler for the 'live_drag' attribute of the
        shell object.

        """
        self.set_live_drag(live_drag)

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
        """ Update the orientation of the splitter.

        """
        wx_orientation = _ORIENTATION_MAP[orientation]
        self.widget.SetOrientation(wx_orientation)

    def set_live_drag(self, live_drag):
        """ Updates the drag state of the splitter.

        """
        if live_drag:
            self.widget.WindowStyle |= wx.SP_LIVE_UPDATE
        else:
            self.widget.WindowStyle &= ~wx.SP_LIVE_UPDATE
            
    def update_children(self):
        """ Update the splitter's children with the current children.

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

