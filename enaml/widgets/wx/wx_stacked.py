#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_container import WXContainer

from ..stacked import AbstractTkStacked


class wxStackedWidget(wx.Choicebook):
    """ A custom control that acts similar to the Qt StackGroup

    The widget starts as a wxChoiceBook but the ChoiceBox widget is 
    hidden as soon as possible. As a result the widget behaves like 
    a QtStackedGroup object with no controls.

    """
    def __init__(self, parent, id=-1, **kwargs):
        super(wxStackedWidget, self).__init__(parent, id=id, **kwargs)
        self.choice_ctrl = self.GetChoiceCtrl()
        self.choice_ctrl.Hide()


class WXStacked(WXContainer, AbstractTkStacked):
    """ Wx implementation of the Stacked Container.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underyling wxStacked control.

        """
        self.widget = wxStackedWidget(parent)

    def initialize(self):
        """ Initialize the stacked widget.

        """
        super(WXStacked, self).initialize()
        self.update_children()
        self.set_index(self.shell_obj.index)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_index_changed(self, index):
        """ Update the widget index with the new value from the shell 
        object.

        """
        self.set_index(index)
        self.shell_obj.size_hint_updated = True

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
    def set_index(self, index):
        """ Set the current visible index of the widget.

        """
        self.widget.SetSelection(index)

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        Override to ask the currently displayed widget for its size hint. 
        Fall back to the minimum size if there is no size hint. If we use
        a constraints-based Container as a child widget, it will only have
        a minimum size set, not a size hint.

        """
        shell = self.shell_obj
        curr_shell = shell.children[shell.index]
        size_hint = curr_shell.size_hint()
        if size_hint == (-1, -1):
            size_hint = tuple(curr_shell.toolkit_widget.GetMinSize())
        return size_hint

    def update_children(self):
        """ Update the wxStackedWidget's children wth the current
        children

        """
        # FIXME: there should be a more efficient way to do this, but 
        # for now just remove all present widgets and add the current 
        # ones. If we use DeleteAllPages(), then the child widgets would
        # be destroyed, which is not the behavior we want.
        shell = self.shell_obj
        widget = self.widget
        while widget.GetPageCount():
            widget.RemovePage(0)
        
        # Reparent all of the child widgets to the new parent. This
        # ensures that any new children are properly parented.
        for child in shell.children:
            child_widget = child.toolkit_widget
            child_widget.Reparent(widget)
            widget.AddPage(child_widget, '')

        # Finally, update the selected index of the of the widget 
        # and notify the layout of the size hint update
        self.set_index(shell.index)
        shell.size_hint_updated = True

