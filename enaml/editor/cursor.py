#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.signaling import Signal


class Caret(object):
    """ A class representing a caret in a text model.

    Zero or more carets are used by a Cursor for editing a text model.
    For performance reasons all attributes on a Caret are public, but
    should only be modified by a Cursor.

    """
    #: A signal emitted when the caret is moved. It has two arguments:
    #: the old location and the new location. Each location is a tuple
    #: of (lineno, position) integers.
    moved = Signal()

    def __init__(self, lineno=0, position=0, desired=0):
        """ Initialize a Caret.

        Parameters
        ----------
        lineno : int, optional
            The line number of the caret. It must be greater than or
            equal to zero. The default is zero.

        position: int, optional
            The position of the caret in the line. It must be greater
            than or equal to zero. The default is zero.

        desired: int, optional
            The desired position of the caret in the line. This is used
            as "memory" for the caret when moving up and down lines. It
            has no effect on the rendering of the Caret. The default is
            zero.

        """
        self.lineno = lineno
        self.position = position
        self.desired = desired

    def update(self, lineno=None, position=None, desired=False):
        """ Update the location of the caret.

        This method will emit the `moved` signal if the updated location
        differs from the current location.

        Parameters
        ----------
        lineno : int, optional
            The new line number of the caret.

        position : int, optional
            The new position of the caret in the line.

        desired : bool, optional
            Whether or not to update the desired position to the given
            position. The default is False.

        """
        old_lineno = self.lineno
        old_position = self.position
        if lineno is None:
            lineno = old_lineno
        if position is None:
            position = old_position
        if desired:
            self.desired = position
        if old_lineno != lineno or old_position != position:
            self.lineno = lineno
            self.position = position
            old = (old_lineno, old_position)
            new = (lineno, position)
            self.moved.emit(old, new)


class Cursor(object):
    """ A class which defines a Cursor for editing a TextInterface.

    When a Cursor is attached to a TextInterface, the interface should
    not be edited by any other code, or the cursor will become out of
    sync with the model.

    """
    #: A signal emitted when a caret is added to the cursor. It carries
    #: two arguments: the lineno, and the position of the caret.
    caret_added = Signal()

    #: A signal emitted when a caret is removed from the cursor. It
    #: carries two arguments: the lineno, and the position of the last
    #: location of the cursor.
    caret_removed = Signal()

    def __init__(self, text):
        """ Initialize a Cursor.

        Parameters
        ----------
        text : TextInterface
            The text interface on which this cursor operates.

        """
        self._text = text
        self._carets = (Caret(),)

    def carets(self):
        """ Get the active carets for this cursor.

        Returns
        -------
        result : tuple
            A tuple of Caret instances being used by the cursor.

        """
        return self._carets

    #--------------------------------------------------------------------------
    # Movement
    #--------------------------------------------------------------------------
    def move(self, lineno, position):
        """ Move the caret to the given lineno and position.

        This operation will remove all but the primary caret.

        Parameters
        ----------
        lineno : int
            The target line number.

        position : int
            The target caret position.

        """
        carets = self._carets
        if len(carets) > 1:
            for caret in carets[1:]:
                self.caret_removed.emit(caret)
            carets = self._carets = carets[:1]
        caret = carets[0]
        text = self._text
        lineno = max(0, min(lineno, text.line_count() - 1))
        line = text.line(lineno)
        pos = max(0, min(position, len(line)))
        caret.update(lineno, pos, True)

    def move_up(self, n=1):
        """ Move the carets up a number of lines.

        When a caret reaches line 0, it will not be moved.

        Parameters
        ----------
        n : int, optional
            The number of lines to move. The default is 1.

        """
        text = self._text
        for caret in self._carets:
            lineno = max(0, caret.lineno - n)
            pos = max(0, min(caret.desired, len(text.line(lineno))))
            caret.update(lineno, pos, False)

    def move_down(self, n=1):
        """ Move the carets down a number a lines.

        When a caret reaches the last line, it will not be moved.

        Parameters
        ----------
        n : int, optional
            The number of lines to move. The default is 1.

        """
        text = self._text
        max_line = text.line_count() - 1
        for caret in self._carets:
            lineno = min(caret.lineno + n, max_line)
            pos = max(0, min(caret.desired, len(text.line(lineno))))
            caret.update(lineno, pos, False)

    def move_left(self, n=1):
        """ Move the carets left a number of characters.

        When a caret reaches the beginning of a line, it will wrap to
        the previous line. If the caret is at the beginning of the text
        model, it will not be moved.

        Parameters
        ----------
        n : int, optional
            The number of characters to move. The default is 1.

        """
        text = self._text
        for caret in self._carets:
            pos = caret.position - n
            lineno = caret.lineno
            if pos < 0:
                lineno -= 1
                while pos < 0 and lineno >= 0:
                    line = text.line(lineno)
                    pos += len(line) + 1
                    lineno -= 1
                lineno += 1
                pos = max(0, pos)
            caret.update(lineno, pos, True)

    def move_right(self, n=1):
        """ Move the carets right a number of characters.

        When a caret reaches the end of a line, it will wrap to the next
        line. If the caret is at the end of the text model, it will not
        be moved.

        Parameters
        ----------
        n : int, optional
            The number of characters to move. The default is 1.

        """
        text = self._text
        max_line = text.line_count() - 1
        for caret in self._carets:
            pos = caret.position + n
            lineno = caret.lineno
            line = text.line(lineno)
            if pos > len(line):
                while True:
                    if lineno == max_line:
                        pos = len(line)
                        break
                    lineno += 1
                    pos -= len(line) + 1
                    line = text.line(lineno)
                    if pos <= len(line):
                        break
            caret.update(lineno, pos, True)

