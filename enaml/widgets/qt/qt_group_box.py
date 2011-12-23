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
    def create(self, parent):
        """ Creates the underlying QGroupBox control.

        """
        self.widget = QResizingGroupBox(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtGroupBox, self).initialize()
        shell = self.shell_obj
        self._set_title(shell.title)
        self._set_flat(shell.flat)
        self._set_title_align(shell.title_align)
        self._reset_layout_margins()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ Update the title of the group box with the new value from the
        shell object.

        """
        # We perform the title update in a relayout context to 
        # prevent flicker and multiple calls to relayout.
        def title_update_closure():
            self._set_title(title)
            self._reset_layout_margins()
        self.shell_obj.relayout_enqueue(title_update_closure)

    def shell_flat_changed(self, flat):
        """ Update the flat flag of the group box with the new value from
        the shell object.

        """
        # We perform the flat update in a relayout context to 
        # prevent flicker and multiple calls to relayout.
        def flat_update_closure():
            self._set_flat(flat)
            self._reset_layout_margins()
        self.shell_obj.relayout_enqueue(flat_update_closure)

    def shell_title_align_changed(self, align):
        """ Update the title alignment to the new value from the shell 
        object.

        """
        self._set_title_align(align)

    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the
        widget.

        """
        dx, dy, dr, db = self._layout_margins
        m = self.widget.contentsMargins()
        contents_margins = (
            m.top() - dy, m.left() - dx, m.right() - dr, m.bottom() - db,
        )
        return contents_margins

    #--------------------------------------------------------------------------
    # Widget Update methods 
    #--------------------------------------------------------------------------
    def _set_title(self, title):
        """ Updates the title of group box.

        """
        self.widget.setTitle(title)
    
    def _set_flat(self, flat):
        """ Updates the flattened appearance of the group box.

        """
        self.widget.setFlat(flat)
    
    def _set_title_align(self, align):
        """ Updates the alignment of the title of the group box.

        """
        qt_align = QT_ALIGNMENTS[align]
        self.widget.setAlignment(qt_align)

