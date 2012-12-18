#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from enaml.signaling import Signal


class CursorInterface(object):
    """ A class which defines a cursor interface for a TextEditor.

    This is a pure abstract class. A cursor is repsonsible for managing
    the positions of zero or more carets. A caret It provides the information necessary
    for a TextEditor to draw the carets at the appropriate location.

    """
    __metaclass__ = ABCMeta

    #: A signal emitted when a caret is added to the cursor. It carries
    #: two arguments: the lineno, and the position of the caret.
    caret_added = Signal()

    #: A signal emitted when a caret is removed from the cursor. It
    #: carries two arguments: the lineno, and the position of the last
    #: location of the cursor.
    caret_removed = Signal()

    @abstractmethod
    def carets(self):
        """ Get the active carets for this cursor.

        Returns
        -------
        result : list of tuple
            A list of 2-tuples of the active carets of the cursor. Each
            tuple is the lineno and position of the caret in the text
            model.

        """
        raise NotImplementedError

