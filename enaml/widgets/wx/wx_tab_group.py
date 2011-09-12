import wx
from wx.lib.agw.flatnotebook import (FlatNotebook, FlatNotebookEvent,
                                     FNB_NODRAG, FNB_NO_NAV_BUTTONS,
                                     FNB_NO_X_BUTTON)
from traits.api import implements

from .wx_stacked_group import WXStackedGroup
from ..tab_group import ITabGroupImpl

wxEVT_FLATNOTEBOOK_PAGE_DROPPED = wx.NewEventType()
EVT_FLATNOTEBOOK_PAGE_DROPPED = \
        wx.PyEventBinder(wxEVT_FLATNOTEBOOK_PAGE_DROPPED, 1)

class CustomFlatNotebook(FlatNotebook):

    pass



class WXTabGroup(WXStackedGroup):
    """ A wxPython implementation of ITab.

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
        self.widget = CustomFlatNotebook(parent=self.parent_widget())
        self.widget.SetWindowStyleFlag(FNB_NO_NAV_BUTTONS | FNB_NO_X_BUTTON)
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

    def parent_movable_changed(self, movable):
        """ Update the movable style in the tab

        Arguments
        ---------
        movable : boolean
            When true the tabs are allowd to be moved around by dragging

        """
        self.set_movable_flag(movable)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def bind(self):
        """ Bind to the flatnotebook widget events.

        """
        pass

    def set_movable_flag(self, movable):
        """ Set the movable style in the widget

        Arguments
        ---------
        movable : boolean
            When true the pages can be moved around

        """
        widget = self.widget
        style = widget.GetWindowStyleFlag()
        if movable:
            style &= ~FNB_NODRAG

        else:
            style |= FNB_NODRAG

        widget.SetWindowStyleFlag(style)

