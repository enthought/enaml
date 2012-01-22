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
    def create(self, parent):
        """ Creates the underlying QSplitter control.

        """
        self.widget = CustomSplitter(parent)

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

    def shell_layout_children_changed(self, children):
        """ The change handler for the 'layout_children' attribute of 
        the shell object.

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

        for child in shell.layout_children:
            child_widget = child.toolkit_widget
            child_widget.Reparent(widget)
            widget.AppendWindow(child_widget)

    def size_hint(self):
        """ Return a size hint for the widget.

        """
        # XXX We're punting here for now. What we need to do is compute
        # the combined size hints for the children using the algorithm
        # implementation in QSplitter::sizeHint
        return (296, 172)

    def set_splitter_sizes(self, sizes):
        """ Set the initial sizes for the children.

        """
        # XXX We're punting here for now. We need to do is implement
        # QSplitter::setSizes
        return

