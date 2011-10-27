#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from wx.lib.agw.flatnotebook import (FlatNotebook, FNB_NODRAG,
                                     FNB_NO_NAV_BUTTONS, FNB_NO_X_BUTTON,
                                     EVT_FLATNOTEBOOK_PAGE_DROPPED,
                                     EVT_FLATNOTEBOOK_PAGE_CHANGED)
from traits.api import implements

from .wx_stacked_group import WXStackedGroup
from ..tab_group import ITabGroupImpl


class WXTabGroup(WXStackedGroup):
    """ A wxPython implementation of ITab.

    The implementation has been tested with the agw library version 0.9.1.

    See Also
    --------
    IStackedGroup

    """
    implements(ITabGroupImpl)

    #---------------------------------------------------------------------------
    # IStackGroupImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Create the wxwidget contrainer for the TabGroup.

        The defualt style sets the tab on top. There are no close buttons
        in the pages and no navigation buttons in the tab control.

        """
        self.widget = FlatNotebook(parent=self.parent_widget())
        self.widget.SetAGWWindowStyleFlag(FNB_NO_NAV_BUTTONS | FNB_NO_X_BUTTON)
        self.bind()

    def initialize_widget(self):
        """ Initialize the StackedGroup widget.

        """
        super(WXTabGroup, self).initialize_widget()
        self.set_movable_flag(self.parent.movable)

    def layout_child_widgets(self):
        """ Layout the contained pages.

        """
        self.widget.Layout()

    def shell_movable_changed(self, movable):
        """ Update the movable style in the tab

        Arguments
        ---------
        movable : boolean
            When true the tabs are allowed to be moved around by dragging

        """
        self.set_movable_flag(movable)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def bind(self):
        """ Bind to the flatnotebook widget events.

        Connect to the page changed event and the page dropped when the user
        has reoredred the notebook pages.
        """
        widget = self.widget
        widget.Bind(EVT_FLATNOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        widget.Bind(EVT_FLATNOTEBOOK_PAGE_DROPPED, self.on_tabs_reordered)

    def set_movable_flag(self, movable):
        """ Set the movable style in the widget

        Arguments
        ---------
        movable : boolean
            When true the pages can be moved around

        """
        widget = self.widget
        style = widget.GetAGWWindowStyleFlag()

        if movable:
            style &= ~FNB_NODRAG

        else:
            style |= FNB_NODRAG

        widget.SetAGWWindowStyleFlag(style)

    def on_page_changed(self, event):
        """ Respond to the page change.

        """
        self.parent.current_index = event.GetSelection()

    def on_tabs_reordered(self, event):
        """ Respond to a re-ordering of the tabs by the user.

        The children pages are re-ordered. Then the current index is updated
        and finally the reordered event is fired.

        """
        children = self.parent.children

        old_position = event.GetOldSelection()
        new_position = min(len(children) - 1, event.GetSelection())

        if old_position != new_position:

            moved_child = children.pop(old_position)
            children.insert(new_position, moved_child)

            self.parent.current_index = new_position
            self.parent.reordered = (old_position, new_position)
