#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import codecs

import blist

from .text_interface import TextInterface
from .text_list_cursor import TextListCursor


class PlainTextList(TextInterface):
    """ A concrete implementation of PlainTextInterface.

    This class uses a blist of string as its internal representation of
    the text model. It performs admirably for models which contain well
    over a millions lines of text and should therefore suit most use
    cases. Instances will typically be created using one of the factory
    class methods.

    Editing of a PlainTextList is performed with PlainTextCursor. Only
    one cursor should ever be active on the model at a time.

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
            lines.extend(line.strip() for line in f)
        self = cls()
        self._lines = lines
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
        lines.extend(unicode(line.strip()) for line in iterable)
        self = cls()
        self._lines = lines
        return self

    def __init__(self):
        """ Initialize a PlainTextList.

        """
        self._lines = blist.blist([u''])
        self._cursor = TextListCursor(self)

    #--------------------------------------------------------------------------
    # Plain Text Interface
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

    def cursor(self):
        """ Get the cursor to use for editing this text model.

        Returns
        -------
        result : TextListCursor
            The cursor to use for editing this text model.

        """
        return self._cursor

