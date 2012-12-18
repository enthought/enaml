#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from enaml.signaling import Signal


class TextInterface(object):
    """ A class which defines a data interface for a TextEditor.

    This is a pure abstract class. It provides enough flexibility that
    implementors are free to choose data structures which suit the task.
    These can be in-memory, on-disk, or a hybrid of the two.

    Line endings will be removed from all input and output to and from
    the interface. Proper handling of line endings is an implementation
    detail for a given use of an interface.

    """
    __metaclass__ = ABCMeta

    #: A signal emitted when characters are inserted into the model. It
    #: carries three arguments: the lineno, the position, and the string
    #: of inserted characters.
    chars_inserted = Signal()

    #: A signal emitted when characters are replaced in the model. It
    #: carries four arguments: the lineno, the position, the string of
    #: removed characters, and the string of inserted characters.
    chars_replaced = Signal()

    #: A signal emitted when characters are removed from the model. It
    #: carries three arguments: the lineno, the position, and the string
    #: of removed characters.
    chars_removed = Signal()

    #: A signal emitted when lines are inserted into the model. It
    #: carries two arguments: the lineno, and the list of inserted lines.
    lines_inserted = Signal()

    #: A signal emitted when lines are replaced in the model. It carries
    #: three arguments: the lineno, the list of removed lines, and the
    #: list of inserted lines.
    lines_replaced = Signal()

    #: A signal emitted when lines are removed from the model. It
    #: carries two aruments: the lineno, and the list of removed lines.
    lines_removed = Signal()

    @abstractmethod
    def __iter__(self):
        """ Get an iterator over the lines in the model.

        Returns
        -------
        result : iterable
            An iterable of all the lines in the model. The lines will
            not have line endings. It is assumed that the model will
            not be modified while this iterator is being consumed.

        """
        raise NotImplementedError

    @abstractmethod
    def line_count(self):
        """ Get the number of lines in the model.

        Returns
        -------
        result : int
            The number of lines in the text model.

        """
        raise NotImplementedError

    @abstractmethod
    def line(self, lineno):
        """ Get the line for the given line number.

        Parameters
        ----------
        int : lineno
            The line number for target line. This is zero-based and must
            be less than the line count.

        Returns
        -------
        result : unicode
            The line of text at the given line number.

        """
        raise NotImplementedError

    @abstractmethod
    def cursor(self):
        """ Get the cursor to use for editing this text model.

        Returns
        -------
        result : CursorInterface
            The cursor to use for editing this text model.

        """
        raise NotImplementedError

