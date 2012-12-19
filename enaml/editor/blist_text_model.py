#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import codecs

import blist

from .text_interface import TextInterface


class BListTextModel(TextInterface):
    """ A concrete implementation of TextInterface.

    This class uses a blist of strings as its internal representation of
    the text model. It performs admirably for models which contain well
    over a millions lines of text and should suit most use cases. An
    instance will typically be created using one of the factory class
    methods.

    """
    @classmethod
    def from_string(cls, string):
        """ Create a PlainTextList from a string.

        Parameters
        ----------
        string : basestring
            The string of data. It will be split into separate lines and
            newline characters will be removed. Non-unicode strings will
            be converted to unicode.

        """
        string = unicode(string)
        lines = blist.blist(string.splitlines())
        self = cls()
        self._lines = lines
        return self

    @classmethod
    def from_file(cls, filename, encoding='utf-8'):
        """ Create a PlainTextList from a file.

        Parameters
        ----------
        filename : basestring
            The name of the file which contains the data. Line endings
            will be removed from the lines as they are read from the
            file. The entire file is read up-front.

        encoding : str, optional
            The encoding of the file. The default is 'utf-8'.

        """
        lines = blist.blist()
        with codecs.open(filename, encoding=encoding) as f:
            lines.extend(line.rstrip() for line in f)
        self = cls()
        self._lines = lines * 10000
        return self

    @classmethod
    def from_iter(cls, iterable):
        """ Create a PlainTextList from an iterable.

        Parameters
        ----------
        iterable : iterable
            An iterable which yields the lines of data. The lines will
            be converted to unicode and stripped of line endings.

        """
        lines = blist.blist()
        lines.extend(unicode(line.rstrip()) for line in iterable)
        self = cls()
        self._lines = lines
        return self

    def __init__(self):
        """ Initialize a PlainTextList.

        """
        self._lines = blist.blist([u''])

    #--------------------------------------------------------------------------
    # Text Interface Implementation
    #--------------------------------------------------------------------------
    def __iter__(self):
        """ Get an iterator over the lines in the model.

        Returns
        -------
        result : iterable
            An iterable of all the lines in the model. The lines will
            not have line endings. It is assumed that the model will
            not be modified while this iterator is being consumed.

        """
        return iter(self._lines)

    def line_count(self):
        """ Get the number of lines in the model.

        Returns
        -------
        result : int
            The number of lines in the text model.

        """
        return len(self._lines)

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
        return self._lines[lineno]

    def insert_chars(self, lineno, position, chars):
        """ Insert characters at the given location.

        This method will emit the `chars_inserted` signal.

        Parameters
        ----------
        lineno : int
            The line number at which to perform the insertion. This is
            zero based and must be less than the line count.

        position : int
            The position in the line at which to insert the characters.
            This is zero based and must be less than or equal to the line
            length.

        chars : unicode
            The text to insert into the line.

        """
        lines = self._lines
        line = lines[lineno]
        edit_line = line[:position] + chars + line[position:]
        lines[lineno] = edit_line
        self.chars_inserted.emit(lineno, position, chars)

    def replace_chars(self, lineno, start, end, chars):
        """ Replace characters at the given location.

        This method will emit the `chars_replaced` signal.

        Parameters
        ----------
        lineno : int
            The line number at which to perform the replacement. This is
            zero based and must be less than the line count.

        start : int
            The starting index of the substring to remove, inclusive.

        end : int
            The ending index of the substring to remove, inclusive.

        chars : unicode
            The text to insert into the line at the starting position.

        """
        lines = self._lines
        line = lines[lineno]
        rem_chars = line[start:end + 1]
        edit_line = line[:start] + chars + line[end + 1:]
        lines[lineno] = edit_line
        self.chars_replaced.emit(lineno, start, rem_chars, chars)

    def remove_chars(self, lineno, start, end):
        """ Remove characters at the given location.

        This method will emit the `chars_removed` signal.

        Parameters
        ----------
        lineno : int
            The line number at which to perform the removal. This is
            zero based and must be less than the line count.

        start : int
            The starting index of the substring to remove, inclusive.

        end : int
            The ending index of the substring to remove, inclusive.

        """
        lines = self._lines
        line = lines[lineno]
        rem_chars = line[start:end + 1]
        edit_line = line[:start] + line[end + 1:]
        lines[lineno] = edit_line
        self.chars_removed.emit(lineno, start, rem_chars)

    def insert_lines(self, lineno, lines):
        """ Insert lines at the given location.

        This method will emit the `lines_inserted` signal.

        Parameters
        ----------
        lineno : int
            The line number at which to insert the lines.

        lines : list
            The list of unicode strings to insert. They must be free of
            line endings.

        """
        these_lines = self._lines
        for line in reversed(lines):
            these_lines.insert(lineno, line)
        self.lines_inserted.emit(lineno, lines)

    def replace_lines(self, start, end, lines):
        """ Replace lines at the given location.

        This method will emit the `lines_replaced` signal.

        Parameters
        ----------
        start : int
            The starting line number of the lines to remove, inclusive.

        end : int
            The ending line number of the lines to remove, inclusive.

        lines : list
            The list of unicode strings to insert. They must be free of
            line endings.

        """
        these_lines = self._lines
        old_lines = list(these_lines[start:end + 1])
        del these_lines[start:end + 1]
        for line in reversed(lines):
            these_lines.insert(start, line)
        self.lines_replaced.emit(start, old_lines, lines)

    def remove_lines(self, start, end):
        """ Remove the lines at the given location.

        This method will emit the `lines_removed` signal.

        Parameters
        ----------
        start : int
            The starting line number of the lines to remove, inclusive.

        end : int
            The ending line number of the lines to remove, inclusive.

        """
        lines = self._lines
        old_lines = list(lines[start:end + 1])
        del lines[start:end + 1]
        self.lines_removed.emit(start, end, old_lines)

