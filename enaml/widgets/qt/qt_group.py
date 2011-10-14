#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_container import QtContainer

from ..group import IGroupImpl

from ...enums import Direction


_QBoxLayoutDirections = {
    Direction.LEFT_TO_RIGHT: QtGui.QBoxLayout.LeftToRight,
    Direction.RIGHT_TO_LEFT: QtGui.QBoxLayout.RightToLeft,
    Direction.BOTTOM_TO_TOP: QtGui.QBoxLayout.BottomToTop,
    Direction.TOP_TO_BOTTOM: QtGui.QBoxLayout.TopToBottom
}


class QtGroup(QtContainer):
    """ A Qt implementation of IGroup.

    The QtGroup uses a QBoxSizer to arrange its child components.

    See Also
    --------
    IGroup

    """
    implements(IGroupImpl)

    #---------------------------------------------------------------------------
    # IGroupImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying sizer for the group. 

        """
        self.widget = self.make_layout(self.parent.direction)
        
    def initialize_widget(self):
        """ Nothing to initialize on a group.

        """
        pass

    def layout_child_widgets(self):
        """ Adds the children of this container to the sizer.

        """
        layout = self.widget
        for child in self.parent.children:
            child_widget = child.toolkit_widget()
            #stretch = child.style.get_property('stretch') or 0
            stretch = 0
            if isinstance(child_widget, QtGui.QLayout):
                layout.addLayout(child_widget, stretch)
            else:
                layout.addWidget(child_widget, stretch)

    def parent_direction_changed(self, direction):
        """ The change handler for the 'direction' attribute on the 
        parent.

        """
        pass
    
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def convert_direction(self, direction):
        """ Translate an Enaml Direction constant to a QBoxLayout Direction
        constant.
        """
        return _QBoxLayoutDirections.get(direction, QtGui.QBoxLayout.LeftToRight)
    
    def make_layout(self, direction):
        """ Creates a QBoxLayout for the given direction value. Not
        meant for public consumption.

        """
        layout = QtGui.QBoxLayout(self.convert_direction(direction))
        return layout
        
    def set_direction(self, direction):
        self.widget.setDirection(self.convert_direction(direction))
        
    def is_reverse_direction(self, direction):
        """ Returns True or False depending on if the given direction
        is reversed from normal. Not meant for public consumption.

        """
        dirs = (Direction.RIGHT_TO_LEFT, Direction.BOTTOM_TO_TOP)
        return direction in dirs

