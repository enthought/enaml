#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_container import QtContainer

from ..container import Container
from ..stacked_group import IStackedGroupImpl
from ..panel import Panel


class QtStackedGroup(QtContainer):
    """ A Qt implementation of StackedGroup.

    See Also
    --------
    StackedGroup

    """
    implements(IStackedGroupImpl)

    #---------------------------------------------------------------------------
    # IStackGroupImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QStackedWidget.

        """
        self.widget = QtGui.QStackedWidget(parent=self.parent_widget())

    def initialize_widget(self):
        """ Initialize the StackedGroup widget.

        """
        self.widget.currentChanged.connect(self.on_current_changed)

    def layout_child_widgets(self):
        """ Lay out the contained pages.

        """
        widget = self.widget
        for child in self.parent.children:
            widget.addWidget(child.toolkit_impl.widget)

        self.set_page(self.parent.current_index)

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
    def on_current_changed(self, index):
        self.parent.current_index = index

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
        result : Container
            The child container at the given index.

        Raises
        ------
        TypeError :
            The index is not an integer.

        IndexError
            No child corresponds to the given index.

        """
        if not isinstance(idx, int):
            raise TypeError('The value "{0}" is not an integer.'.format(idx))

        return self.parent.children[idx]

    def index_of(self, child):
        """ Returns the index corresponding to the given child container.

        Arguments
        ---------
        child : Container
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
        if not isinstance(child, Panel):
            message = ('Input argument child is not a Panel'
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
        self.widget.setCurrentIndex(index)
