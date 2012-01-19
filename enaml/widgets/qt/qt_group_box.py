#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore
from .qt_container import QtContainer
from .qt_resizing_widgets import QResizingGroupBox

from ..group_box import AbstractTkGroupBox


QT_ALIGNMENTS = dict(
    left=QtCore.Qt.AlignLeft,
    right=QtCore.Qt.AlignRight,
    center=QtCore.Qt.AlignHCenter,
)


class QtGroupBox(QtContainer, AbstractTkGroupBox):
    """ A Qt4 implementation of GroupBox.

    """
    #: Don't use a widget item to compute the layout rect for a group
    #: box, it results in not enough space around neighbors.
    # XXX investigate this further, it may have to do with constraints
    # specification on the group box and how neighbors are anchored.
    use_widget_item_for_layout = False
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QGroupBox control.

        """
        self.widget = QResizingGroupBox(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtGroupBox, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_flat(shell.flat)
        self.set_title_align(shell.title_align)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ Update the title of the group box with the new value from the
        shell object.

        """
        # We perform the title update in a relayout context to 
        # prevent flicker and multiple calls to relayout.
        self.shell_obj.request_relayout_task(self.set_title, title)

    def shell_flat_changed(self, flat):
        """ Update the flat flag of the group box with the new value from
        the shell object.

        """
        # We perform the flat update in a relayout context to 
        # prevent flicker and multiple calls to relayout.
        self.shell_obj.request_relayout_task(self.set_flat, flat)

    def shell_title_align_changed(self, align):
        """ Update the title alignment to the new value from the shell 
        object.

        """
        self.set_title_align(align)

    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the
        widget.

        """
        m = self.widget.contentsMargins()
        return (m.top(), m.left(), m.right(), m.bottom())

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

