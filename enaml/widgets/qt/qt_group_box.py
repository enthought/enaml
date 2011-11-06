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

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------

    def create(self):
        """ Creates the underlying QGroupBox control.

        """
        self.widget = QResizingGroupBox(self.parent_widget())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtGroupBox, self).initialize()
        shell = self.shell_obj
        self.shell_title_changed(shell.title)
        self.shell_flat_changed(shell.flat)
        self.shell_title_align_changed(shell.title_align)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ Update the title of the group box with the new value from the
        shell object.

        """
        self.widget.setTitle(title)
        self.shell_obj.set_needs_update_constraints()

    def shell_flat_changed(self, flat):
        """ Update the flat flag of the group box with the new value from the
        shell object.

        """
        self.widget.setFlat(flat)
        self.shell_obj.set_needs_update_constraints()

    def shell_title_align_changed(self, align):
        """ Update the title alignment to the new value from the shell object.

        """
        qt_align = QT_ALIGNMENTS[align]
        self.widget.setAlignment(qt_align)

    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the widget.

        """
        margins = self.widget.contentsMargins()
        return (margins.top(), margins.left(), margins.right(), margins.bottom())
