#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements

from .wx_container import WXContainer
from ..stacked_group import IStackedGroupImpl


class wxStackedGroup(wx.Choicebook):
    """ A custom control that acts similar to the Qt StackGroup

    The widget starts as a wxChoiceBook but the ChoiceBox widget is hidden
    as soon as possible. As a result the widget behaves like a
    QtStackedGroup object with no controls.

    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                       size=wx.DefaultSize, style=0, name=''):
        """ Initialize StackedGroup

        """
        super(wxStackedGroup, self).__init__(parent, id, pos,
                                                size, style, name)
        self.choice_ctrl = self.GetChoiceCtrl()
        self.choice_ctrl.Hide()


class WXStackedGroup(WXContainer):
    """ A wxPython implementation of IStackedGroup.

    See Also
    --------
    IStackedGroup

    """
    implements(IStackedGroupImpl)

    #---------------------------------------------------------------------------
    # IStackGroupImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Create the wxwidget contrainer for the StackGroup.

        """
        self.widget = wxStackedGroup(parent=self.parent_widget())

    def initialize_widget(self):
        """ Initialize the StackedGroup widget.

        """
        widget = self.widget
        for child in self.parent.children:
            widget.AddPage(child.toolkit_impl.widget, child.name)

        self.set_page(self.parent.current_index)

    def layout_child_widgets(self):
        """ Layout the contained pages.

        """
        self.widget.Layout()

    def shell_current_index_changed(self, current_index):
        """ Update the visible page

        Arguments
        ---------
        current_index : int
            The index of the page to make visible
        """
        self.set_page(current_index)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def child_at(self, idx):
        """ Returns the child container at the given index.

        Arguments
        ---------
        idx : int
            The zero based index to use to lookup the child container.
            It may be negative, in which case the lookup will be
            from the end of the stack.

        Returns
        -------
        result : WXContainer
            The child container at the given index.

        Raises
        ------
        TypeError :
            The index is not an integer.

        IndexError :
            No child corresponds to the given index.

        """
        return self.children[idx]

    def index_of(self, child):
        """ Returns the index corresponding to the given child container.

        Arguments
        ---------
        child : WXContainer
            The child container to lookup.

        Returns
        -------
        result : int
            The index of the given child container.

        Raises
        ------
        TypeError :
            The child is not a Container.

        IndexError :
            The child does not exist in the group.

        """
        if not isinstance(child, WXContainer):
            message = ('Input argument child is not a WXContainer '
                      'type but a {0}'.format(type(child)))
            raise TypeError(message)

        try:
            index = self.children.index(child)
        except ValueError:
            message = 'The child {0} was not found'.format(child)
            raise IndexError(message)

        return index

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def set_page(self, index):
        """ Set the visible page

        Arguments
        ---------
        index : int
            Index of the page to select

        """
        self.widget.SetSelection(index)
