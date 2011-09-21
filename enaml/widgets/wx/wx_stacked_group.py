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
        for child_wrapper, name in self.wrap_child_containers():
            widget.AddPage(child_wrapper, name)

        self.set_page(self.parent.current_index)

    def layout_child_widgets(self):
        """ Layout the contained pages.

        """
        self.widget.Layout()

    def parent_current_index_changed(self, current_index):
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

    def wrap_child_containers(self):
        """ Yield a "page" for each child container.

        The wxStackedWidget doesn't support adding Sizers directly. Thus
        The wxcontainers (i.e. sizers) need to be wrapped inside a dummy
        wxPanel object. The parent of all the sizer's widgets is changed
        to the dummy wxPanel. However since it is possible the some of the
        children are sizers themselves we need to wrapp them into dummy
        wxPanel widgets also.

        .. note:: Currenlty it is not supported to have more than one
           container group inside on of the children containers. Thus the
           following example will fail with an attribute error::

                Window main:
                    title = "StackedGroup"
                    Panel:
                        StackedGroup:
                            current_index << 1 if page2.checked else 0
                            HGroup:
                                name = "page 1"
                                VGroup:
                                    Label:
                                        text = "This is group 1"
                                    Label:
                                        text = "This is group 1"
                                HGroup:
                                    Label:
                                        text = "This is group 2"
                                    Label:
                                        text = "This is group 2"
                            VGroup:
                                name = "page 2"
                                Label:
                                    text = "Well, this is not page 1!!!!"
                        HGroup:
                            CheckBox page2:
                                text = "page 2"

        """
        for child_container in self.parent.children:

            child_wrapper = wx.Panel(self.widget)
            sizer = child_container.toolkit_impl.widget

            for child in child_container.children:
                child.toolkit_impl.widget.Reparent(child_wrapper)

##                try:
##                    child.toolkit_impl.widget.Reparent(child_wrapper)
##                except AttributeError:
##                    wrapped_child = child.wrap_child_containers()
##                    wrapped_child.Reparent(child_wrapper)

            child_wrapper.SetSizer(sizer)
            yield child_wrapper, child_container.name


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
        return self.parent.children[idx]

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
            index = self.parent.children.index(child)
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
