#------------------------------------------------------------------------------
# Copyright (c) 2012, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
import wx
from wx.lib.splitter import MultiSplitterWindow

from .wx_constraints_widget import WxConstraintsWidget
from .wx_split_item import WxSplitItem


_ORIENTATION_MAP = {
    'horizontal': wx.HORIZONTAL,
    'vertical': wx.VERTICAL,
}


class wxSplitter(MultiSplitterWindow):
    """ A wx.lib.splitter.MultiSplitterWindow subclass that changes
    the behavior of resizing neighbors to be consistent with Qt.

    TODO - Fix the problem with the splitter not resizing its children
           smaller when possible when the splitter window shrinks.
           Fix the problem with initial sash positions.

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
        # TODO implement this properly (or just rewrite this entire
        # control, because like everything else in Wx, it's crap).
        event.m_shiftDown = True
        return super(wxSplitter, self)._OnMouse(event)


class WxSplitter(WxConstraintsWidget):
    """ A Wx implementation of an Enaml Splitter.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wxSplitter widget.

        """
        return wxSplitter(parent)

    def create(self, tree):
        """ Create and initialize the splitter control.
        """
        super(WxSplitter, self).create(tree)
        self.set_orientation(tree['orientation'])
        self.set_live_drag(tree['live_drag'])

    def init_layout(self):
        """ Handle the layout initialization for the splitter.

        """
        super(WxSplitter, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, WxSplitItem):
                widget.AppendWindow(child.widget())
        widget.SizeWindows()

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a WxSplitter.

        """
        if isinstance(child, WxSplitItem):
            widget = child.widget()
            self.widget().DetachWindow(widget)
            widget.Hide()
            self.size_hint_updated()

    def child_added(self, child):
        """ Handle the child added event for a WxSplitter.

        """
        if isinstance(child, WxSplitItem):
            self.widget().AppendWindow(child.widget())
            self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Message Handler Methods
    #--------------------------------------------------------------------------
    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])
        self.size_hint_updated()

    def on_action_set_live_drag(self, content):
        """ Handle the 'set_live_drag' action from the Enaml widget.

        """
        self.set_live_drag(content['live_drag'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Update the orientation of the splitter.

        """
        wx_orientation = _ORIENTATION_MAP[orientation]
        widget = self.widget()
        widget.SetOrientation(wx_orientation)
        widget.SizeWindows()

    def set_live_drag(self, live_drag):
        """ Updates the drag state of the splitter.

        """
        widget = self.widget()
        if live_drag:
            widget.WindowStyle |= wx.SP_LIVE_UPDATE
        else:
            widget.WindowStyle &= ~wx.SP_LIVE_UPDATE

