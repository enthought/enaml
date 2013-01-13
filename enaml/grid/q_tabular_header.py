#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QFrame

from .tabular_model import TabularModel, NullModel


class QTabularHeader(QFrame):
    """ A base class for creating headers for use by a QTabularView.

    This class must be subclassed in order to be useful. The subclass
    must implement the abstract api defined below. A subclass should
    also implement `paintEvent` in order to render the header.

    The abstract methods defined below will be called *often* by the
    QTabularView. Subclasses should make a concerted effort to ensure
    the implementations are as efficient as possible.

    All visual indices reported by a header must be contiguous. That
    is, if visual indices 0 and 5 exist, then 1, 2, 3, and 4 must also
    exist and in that order. It is the responsibility of the header to
    maintain any relevant internal state for hidden and moved sections.
    The QTabularView always treats a header as a continuous monontonic
    block of visible sections.

    The QTabularView will use the trailing pixel of each section as
    the space to draw the grid line.

    """
    def __init__(self, orientation, parent=None):
        """ Initialize a QTabularHeader.

        Parameters
        ----------
        orientation : Qt.Orientation
            The orientation of the header. This must be either
            Qt.Horizontal or Qt.Vertical.

        parent : QWidget, optional
            The parent of this header, or None of the header has
            no parent.

        """
        super(QTabularHeader, self).__init__(parent)
        assert orientation in (Qt.Horizontal, Qt.Vertical)
        self._orientation = orientation
        self._model = NullModel()
        self._offset = 0

    def orientation(self):
        """ Get the orientation of the header.

        Returns
        -------
        result : Qt.Orientation
            The orientation of the header. This must be either
            Qt.Horizontal or Qt.Vertical.

        """
        return self._orientation

    def model(self):
        """ Get the model associated with the header.

        Returns
        -------
        result : TabularModel
            The model associated with the header.

        """
        return self._model

    def setModel(self, model):
        """ Set the model associated with the header.

        This method may be overridden by subclasses for more control.

        Parameters
        ----------
        model : TabularModel
            The tabular model to use with the header.

        """
        assert isinstance(model, TabularModel)
        self._model = model

    def offset(self):
        """ Get the current offset of the header.

        The offset of the header is the offset into the virtual length
        for the current zero position of the viewport.

        Returns
        -------
        result : int
            The current offset of the header. This will always be
            greater than or equal to zero.

        """
        return self._offset

    def setOffset(self, offset):
        """ Set the current offset of the header.

        This method should be overridden by subclasses to issue the
        appropriate scroll or update request for painting.

        Parameters
        ----------
        offset : int
            The desired offset of the header. This must be bounded by
            zero and the header length.

        """
        self._offset = offset

    def logicalIndexAt(self, position):
        """ Get the logical index which overlaps the position.

        Parameters
        ----------
        position : int
            The visual pixel position to map to a logical index. This
            must always be bounded by zero and the header length.

        Returns
        -------
        result : int
            The logical index for the visual position. On success, this
            will be greater than or equal to zero. On failure, -1 is
            returned indicating the position is out of bounds.

        """
        index = self.visualIndexAt(position)
        if index == -1:
            return index
        return self.logicalIndex(index)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def count(self):
        """ Get the number of visible sections in the header.

        The visible sections are the sections of the header which can
        be viewed by scrolling to the extents of the grid. This count
        should not include sections which have been explicitly hidden
        by the user.

        Returns
        -------
        result : int
            The number of visible sections in the header.

        """
        raise NotImplementedError

    def length(self):
        """ Get the total visible length of the header.

        This is the length of all visible sections in the header. The
        length should not include sections which have been explicitly
        hidden by the user.

        Returns
        -------
        result : int
            The total visible length of the header.

        """
        raise NotImplementedError

    def sectionSize(self, visual_index):
        """ Get the size for a given visual section.

        Parameters
        ----------
        visual_index : int
            The visual index of the section. This must be bounded by
            zero and the header count.

        Returns
        -------
        result : int
            The size of the given section.

        """
        raise NotImplementedError

    def sectionPosition(self, visual_index):
        """ Get the pixel position for a given visual index.

        Parameters
        ----------
        visual_index : int
            The visual index of the section. This must be bounded by
            zero and the header count.

        Returns
        -------
        result : int
            The position of the given section. It will not be adjusted
            for the header offset.

        """
        raise NotImplementedError

    def trailingSpan(self, length):
        """ Get the number of trailing items covered by a given length.

        This value is used by QTabularView when scrolling per item
        in order to set the ending scroll position.

        Parameters
        ----------
        length : int
            The length of the given coverage request.

        Returns
        -------
        result : int
            The number of items at the end of the end of the header
            covered by the given length.

        """
        raise NotImplementedError

    def visualIndexAt(self, position):
        """ Get the visual index which overlaps the position.

        Parameters
        ----------
        position : int
            The visual pixel position to map to a visual index. This
            must be bounded by zero and the header length.

        Returns
        -------
        result : int
            The visual index for the visual position. On success, this
            will be greater than or equal to zero. On failure, -1 is
            returned indicating the position is out of bounds.

        """
        raise NotImplementedError

    def visualIndex(self, logical_index):
        """ Get the visual index for a given logical index.

        Parameters
        ----------
        logical_index : int
            The logical model index to map to a header visual index.
            This must be bounded by zero and the relevant model row
            or column count.

        Returns
        -------
        result : int
            The visual index for the model index. On success, this will
            be greater than or equal to zero. On failure, -1 is returned
            indicating that logical index has no visual index; i.e that
            logical index is hidden.

        """
        raise NotImplementedError

    def logicalIndex(self, visual_index):
        """ Get the logical index for a given visual index.

        Parameters
        ----------
        visual_index : int
            The visual header index to map to a model logical index.
            This must be bounded by zero and the header count.

        Returns
        -------
        result : int
            The logical model index for the visual header index.

        """
        raise NotImplementedError

