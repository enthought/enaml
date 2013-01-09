#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.signaling import Signal

from .indexing import Position


class Cursor(object):
    """ A class representing a cursor in a text document.

    The `position` of a Cursor should be considered read-only by
    external consumers.

    """
    #: A signal emitted when the cursor is moved in the text document.
    #: Handlers must accept two arguments: the old Postion and the
    #: new Position of the cursor in the document.
    moved = Signal()

    def __init__(self, document):
        """ Initialize a Cursor.

        Parameters
        ----------
        document : Document
            The document on which this cursor should operate.

        """
        self._document = document
        self._position = Position(0, 0)
        self._desired = 0
        document.modified.connect(self._on_document_modified)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _on_document_modified(self, mod):
        """ A handler for the `modified` signal on the document.

        """
        pass

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def position(self):
        """ A read-only property which returns the cursor Position.

        """
        return self._position

    #--------------------------------------------------------------------------
    # Movement
    #--------------------------------------------------------------------------
    def move(self, position):
        """ Move the caret to the given lineno and position.

        Parameters
        ----------
        position : Position
            The absolute position in the document to which the cursor
            should be moved. This position will be clipped to the
            bounds of the document.

        """
        doc = self._document
        old = self._position
        lineno = max(0, min(position.lineno, len(doc) - 1))
        line = doc[lineno]
        column = max(0, min(position.column, len(line)))
        new = Position(lineno, column)
        if old != new:
            self._position = new
            self._desired = column
            self.moved.emit(old, new)

    def move_up(self, n=1):
        """ Move the cursor up a number of lines.

        When the cursor reaches line 0, it will not be moved.

        Parameters
        ----------
        n : int, optional
            The number of lines to move. The default is 1.

        """
        doc = self._document
        old = self._position
        lineno = max(0, old.lineno - n)
        column = max(0, min(self._desired, len(doc[lineno])))
        new = Position(lineno, column)
        if old != new:
            self._position = new
            self.moved.emit(old, new)

    def move_down(self, n=1):
        """ Move the cursor down a number a lines.

        When the cursor reaches the last line, it will not be moved.

        Parameters
        ----------
        n : int, optional
            The number of lines to move. The default is 1.

        """
        doc = self._document
        old = self._position
        max_line = len(doc) - 1
        lineno = min(old.lineno + n, max_line)
        column = max(0, min(self._desired, len(doc[lineno])))
        new = Position(lineno, column)
        if old != new:
            self._position = new
            self.moved.emit(old, new)

    def move_left(self, n=1):
        """ Move the cursor left a number of characters.

        When the cursor reaches the beginning of a line, it will wrap to
        the previous line. If the cursor is at the beginning of the text
        document, it will not be moved.

        Parameters
        ----------
        n : int, optional
            The number of characters to move. The default is 1.

        """
        doc = self._document
        old = self._position
        lineno = old.lineno
        column = old.column - n
        while column < 0 and lineno > 0:
            lineno -= 1
            line = doc[lineno]
            column += len(line) + 1
        column = max(0, column)
        new = Position(lineno, column)
        if old != new:
            self._position = new
            self._desired = column
            self.moved.emit(old, new)

    def move_right(self, n=1):
        """ Move the cursor right a number of characters.

        When the cursor reaches the end of a line, it will wrap to the
        next line. If the cursor is at the end of the text model, it
        will not be moved.

        Parameters
        ----------
        n : int, optional
            The number of characters to move. The default is 1.

        """
        doc = self._document
        old = self._position
        lineno = old.lineno
        column = old.column + n
        last_line = len(doc) - 1
        line_length = len(doc[lineno])
        while column > line_length and lineno < last_line:
            column -= line_length + 1
            lineno += 1
            line_length = len(doc[lineno])
        column = min(column, line_length)
        new = Position(lineno, column)
        if old != new:
            self._position = new
            self._desired = column
            self.moved.emit(old, new)

    #--------------------------------------------------------------------------
    # Editing
    #--------------------------------------------------------------------------
    def insert(self, text):
        doc = self._document
        doc.insert_inline(self._position, text)
        new = Position(self.position.lineno, self.position.column + 1)
        old = self._position
        self._position = new
        self.moved.emit(old, new)

    def newline(self):
        doc = self._document
        old = self._position
        new = self._position = Position(old.lineno + 1, 0)
        doc.insert_newline(old)
        self.moved.emit(old, new)

    def backspace(self):
        doc = self._document
        old = self._position
        column = old.column
        lineno = old.lineno
        if column > 0:
            self._position = new = Position(lineno, column - 1)
            self._desired = column - 1
            doc.remove_inline(lineno, column - 1, column)
            self.moved.emit(old, new)
        elif lineno > 0:
            line = doc[lineno - 1]
            line_length = len(line)
            self._position = new = Position(lineno - 1, line_length)
            self._desired = line_length
            doc.remove_newline(lineno - 1)
            self.moved.emit(old, new)

    def delete(self):
        doc = self._document
        old = self._position
        column = old.column
        lineno = old.lineno
        line = doc[lineno]
        if column >= len(line):
            doc.remove_newline(lineno)
        else:
            doc.remove_inline(lineno, column, column + 1)

