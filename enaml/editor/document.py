#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import codecs

import blist

from enaml.signaling import Signal

from .indexing import Position
from .modification import (
    InsertNewline, InsertInline, InsertLines, RemoveNewline, RemoveLines,
    RemoveInline
)


class Document(object):
    """ A class which represents a plain text document.

    A Document uses a blist of Line instances as the internal model of
    the text document. Instances of this class will typically be created
    with one of the factory class methods.

    For performance reasons, bounds checking is not performed by methods
    which modify the document; it is assumed that all parameters passed
    to the modification methods contain valid indices.

    """
    #: A signal emitted when the document is modified. Handlers must
    #: accept a single argument which is an instance of Modification.
    #: It represents a change made to the document and provides a means
    #: to undo and redo the change and compute relevant change effects.
    modified = Signal()

    @classmethod
    def from_string(cls, string):
        """ Create a Document from a string.

        Parameters
        ----------
        string : basestring
            The string of data. It will be split into separate lines and
            newline characters will be removed. Non-unicode strings will
            be converted to unicode.

        Returns
        -------
        result : Document
            A new document instance containing the given text.

        """
        string = unicode(string)
        data = blist.blist(string.splitlines())
        self = cls()
        self._data = data
        return self

    @classmethod
    def from_file(cls, filename, encoding='utf-8'):
        """ Create a Document from an on-disk file.

        Parameters
        ----------
        filename : basestring
            The name of the file which contains the data. Line endings
            will be removed from the lines as they are read from the
            file. The entire file is read into memory immediately.

        encoding : str, optional
            The encoding of the file. The default is 'utf-8'.

        Returns
        -------
        result : Document
            A new document instance containing the file text.

        """
        data = blist.blist()
        with codecs.open(filename, encoding=encoding) as f:
            data.extend(line.rstrip(u'\r\n') for line in f)
        self = cls()
        self._data = data
        return self

    @classmethod
    def from_iter(cls, iterable):
        """ Create a Document from an iterable.

        Parameters
        ----------
        iterable : iterable
            An iterable which yields the lines of data. The lines will
            be converted to unicode and stripped of line endings.

        Returns
        -------
        result : Document
            A new document instance containing the iterabl text.

        """
        data = blist.blist()
        data.extend(unicode(line).rstrip(u'\r\n') for line in iterable)
        self = cls()
        self._data = data
        return self

    def __init__(self):
        """ Initialize a Document.

        """
        self._data = blist.blist()

    def __len__(self):
        """ Get the number of lines in the document.

        Returns
        -------
        result : int
            The number of lines in the document.

        """
        return len(self._data)

    def __iter__(self):
        """ Get an iterator over the lines in the document.

        Returns
        -------
        result : iterable
            An iterable of all the lines in the document. The lines will
            not have line endings and the document must not be modified
            while the iterator is being consumed.

        """
        return iter(self._data)

    def __getitem__(self, index):
        """ Get a line or slice of lines from the document.

        Parameters
        ----------
        index : int or slice
            The line number or slice to retrieve from the document.

        Returns
        -------
        result : unicode or iterable
            The requested line or slice of lines from the document. Lines
            will not contain newline characters.

        """
        return self._data[index]

    def insert(self, position, text):
        """ Insert text at the given location.

        Parameters
        ----------
        position : Position
            The position in the document at which to insert the text.

        text : unicode
            The text to insert into the line. If the text has newline
            characters, it will be split into multiple lines. If it is
            known that the string does not contain newline characters,
            use the faster `insert_inline` method instead.

        """
        pass

    def insert_newline(self, position):
        """ Insert a newline into the document at the given location.

        Parameters
        ----------
        position : Position
            The position at which to insert the newline.

        """
        data = self._data
        lineno = position.lineno
        column = position.column
        line = data[lineno]
        leading = line[:column]
        trailing = line[column:]
        data[lineno] = leading
        data.insert(lineno + 1, trailing)
        mod = InsertNewline(position)
        self.modified.emit(mod)

    def insert_inline(self, position, text):
        """ Insert text inline at the given location.

        Parameters
        ----------
        position : Position
            The position at which to insert the text.

        text : unicode
            The text to insert into the line. It must not contain any
            newline characters.

        """
        data = self._data
        lineno = position.lineno
        column = position.column
        line = data[lineno]
        edit_line = line[:column] + text + line[column:]
        data[lineno] = edit_line
        mod = InsertInline(position, text)
        self.modified.emit(mod)

    def insert_lines(self, lineno, lines):
        """ Insert lines at the given location.

        Parameters
        ----------
        lineno : int
            The line number at which to insert the lines.

        lines : iterable
            An iterable of unicode strings to insert. The strings must
            not contain any newline characters.

        """
        lines = list(lines)
        insert = self._data.insert
        for line in reversed(lines):
            insert(lineno, line)
        mod = InsertLines(lineno, lines)
        self.modified.emit(mod)

    def remove(self, span):
        """ Remove a substring from the document.

        Parameters
        ----------
        span : Span
            The span of text to remove from the document.

        """
        pass

    def remove_newline(self, lineno):
        """ Remove the newline character at end of line for the given
        line number.

        Parameters
        ----------
        lineno : int
            The line number at which to remove the newline character.
            The line will be joined with immediately following line.

        """
        data = self._data
        this_line = data[lineno]
        next_line = data[lineno + 1]
        edit_line = this_line + next_line
        del data[lineno + 1]
        data[lineno] = edit_line
        position = Position(lineno, len(this_line))
        mod = RemoveNewline(position)
        self.modified.emit(mod)

    def remove_inline(self, lineno, start_column, end_column):
        """ Remove text inline at the given location.

        Parameters
        ----------
        lineno : int
            The line number at which to perform the removal.

        start_column : int
            The starting column of the substring to remove, inclusive.

        end_column : int
            The ending column of the substring to remove, exclusive.

        """
        data = self._data
        line = data[lineno]
        text = line[start_column:end_column]
        edit_line = line[:start_column] + line[end_column:]
        data[lineno] = edit_line
        position = Position(lineno, start_column)
        mod = RemoveInline(position, text)
        self.modified.emit(mod)

    def remove_lines(self, start_lineno, end_lineno):
        """ Remove the lines at the given location.

        Parameters
        ----------
        start_lineno : int
            The starting line number of the lines to remove, inclusive.

        end_lineno : int
            The ending line number of the lines to remove, exclusive.

        """
        data = self._data
        rem_lines = list(data[start_lineno:end_lineno])
        del data[start_lineno:end_lineno]
        mod = RemoveLines(start_lineno, rem_lines)
        self.lines_removed.emit(mod)

    def replace(self, span, text):
        """ Replace a substring of text in the document.

        Parameters
        ----------
        span : Span
            A span indicating the substring of text to remove.

        text : unicode
            The text which will replace the removed substring. If the
            text has newline characters, it will be split into multiple
            lines.

        """
        pass

