#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from bisect import bisect_right

from enaml.qt.qt.QtCore import Qt
from .q_tabular_header import QTabularHeader


class QVariableSizeHeader(QTabularHeader):
    """ An implementation of QTabularHeader to allow variable
    row widths and column heights.
    """

    def __init__(self, orientation, parent=None):
        """ Initialize a QVariableSizeHeader.

        Parameters
        ----------
        orientation : Qt.Orientation
            The orientation of the header. This must be either
            Qt.Horizontal or Qt.Vertical.

        parent : QWidget, optional
            The parent of this header, or None of the header has
            no parent.

        """
        super(QVariableSizeHeader, self).__init__(orientation, parent)
        self._count = 0
        self._length = 0
        if self.orientation() == Qt.Horizontal:
            self._header_size = 17
            self.setSectionSize(70)
        else:
            self._header_size = 70
            self.setSectionSize(17)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setModel(self, model):
        """ A reimplemented parent class method.

        Parameters
        ----------
        model : TabularModel
            The tabular model to use with the header.

        """
        super(QVariableSizeHeader, self).setModel(model)
        if self.orientation() == Qt.Horizontal:
            count = model.column_count()
        else:
            count = model.row_count()
        self._count = count
        #self._length = self._section_pos[-1]

    def setHeaderSize(self, size):
        """ Set the display size for the header.

        Parameters
        -------
        result : int
            The size to use by QTabularView when displaying the header.
            For horizontal headers, this will be the header height. For
            vertical headers, this will be the header width. This must
            be greater than or equal to zero.

        """
        self._header_size = size

    def setSectionSize(self, size):
        """ Set the section size to use with the header.

        Parameters
        ----------
        size : list or int
            The section size to use for each section in the header.
            List items must be integers greater than or equal to zero.
            If size is an integer, set a constant width for sections.

        """
        if isinstance(size, int):
            size = [size] * self._count
        assert isinstance(size, list)
        assert len(size) == self._count
        # cumulative sum for positions
        # len(_section_pos) will be size + 1 to allow for end of header
        counter = 0
        section_pos = []
        for value in size:
            section_pos.append(counter)
            counter += value
        section_pos.append(counter)
        self._section_pos = section_pos
        self._length = counter

    #--------------------------------------------------------------------------
    # Abstract API implementation.
    #--------------------------------------------------------------------------
    def count(self):
        """ Get the number of visible sections in the header.

        This count does not include hidden sections.

        Returns
        -------
        result : int
            The number of visible sections in the header.

        """
        return self._count

    def length(self):
        """ Get the total visible length of the header in pixels.

        This length does not include hidden sections.

        Returns
        -------
        result : int
            The total visible length of the header.

        """
        return self._length

    def headerSize(self):
        """ Get the display size for the header.

        Returns
        -------
        result : int
            The size to use by QTabularView when displaying the header.
            For horizontal headers, this will be the header height. For
            vertical headers, this will be the header width.

        """
        return self._header_size

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
        return self._section_pos[visual_index + 1] - self._section_pos[visual_index]

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
        return self._section_pos[visual_index]

    def trailingSpan(self, length):
        """ Get the number of trailing items covered by a given length
        from the back of the header.

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
        return self._count - bisect_right(self._section_pos, self._length - length)

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
        idx = bisect_right(self._section_pos, position)
        if idx <= self._count:
            return idx - 1
        return -1

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
        # XXX section moving and hiding not yet supported
        return logical_index

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
        # XXX section moving and hiding not yet supported.
        return visual_index
