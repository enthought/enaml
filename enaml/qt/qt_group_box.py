#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore
from .qt_container import QtContainer
from .qt_resizing_widgets import QResizingGroupBox
from .qt.QtCore import QSize

from ..layout.geometry import Box


QT_ALIGNMENTS = dict(
    left=QtCore.Qt.AlignLeft,
    right=QtCore.Qt.AlignRight,
    center=QtCore.Qt.AlignHCenter,
)


class QGroupBox(QResizingGroupBox):
    """ A subclass of QResizingBox which allows the default sizeHint
    to be overridden by calling 'setSizeHint'.

    This functionality is used by the QtContainer to override the 
    size hint with a value computed from the constraints layout 
    manager.

    """
    #: An invalid QSize used as the default value for class instances.
    _size_hint = QSize()

    def sizeHint(self):
        """ Computes the size hint from the given QtContainer using the
        containers minimimum computed size. If the container returns an
        invalid size, the superclass' sizeHint will be used.

        """
        hint = self._size_hint
        if not hint.isValid():
            hint = super(QGroupBox, self).sizeHint()
        return hint

    def setSizeHint(self, hint):
        """ Sets the size hint to use for this resizing frame.

        """
        self._size_hint = hint

    def minimumSizeHint(self):
        """ Returns the minimum size hint of the container.

        The minimum size hint for a QContainer is conceptually the
        same as its size hint, so we just return that value. Overriding
        this method allows QContainers to function properly as children
        of scroll areas and splitters.

        """
        return self.sizeHint()


class QtGroupBox(QtContainer):
    """ A Qt4 implementation of GroupBox.

    """
    #: Don't use a widget item to compute the layout rect for a group
    #: box, it results in not enough space around/above neighbors.
    use_widget_item_for_layout = False
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QGroupBox control.

        """
        self.widget = QGroupBox(self.parent_widget)

    def initialize(self, attrs):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtGroupBox, self).initialize(attrs)
        self.set_title(attrs['title'])
        self.set_flat(attrs['flat'])
        self.set_title_align(attrs['title_align'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_title_align(self, content):
        """ Handle the 'set_title_align' action from the Enaml widget.

        """
        self.set_title_align(content['title_align'])

    def on_action_set_flat(self, content):
        """ Handle the 'set_flat' action from the Enaml widget.

        """
        self.set_flat(content['flat'])

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the
        widget.

        """
        m = self.widget.contentsMargins()
        return Box(m.top(), m.right(), m.bottom(), m.left())

    #--------------------------------------------------------------------------
    # Widget Update methods 
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Updates the title of group box.

        """
        self.widget.setTitle(title)
    
    def set_flat(self, flat):
        """ Updates the flattened appearance of the group box.

        """
        self.widget.setFlat(flat)
    
    def set_title_align(self, align):
        """ Updates the alignment of the title of the group box.

        """
        qt_align = QT_ALIGNMENTS[align]
        self.widget.setAlignment(qt_align)

