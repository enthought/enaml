#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from .indexing import Position, Span


class Modification(object):
    """ An abstract base class for Document modifications.

    A modification represents a change to a Document. It is capable of
    applying and reverting the given change, as well as computing some
    relevant document effects related to the change.

    """
    __metaclass__ = ABCMeta

    __slots__ = ()

    @abstractmethod
    def apply(self, document):
        """ Apply the change represented by this modification.

        This is an abstract method which must be implemented by
        subclasses.

        Parameters
        ----------
        document : Document
            The document instance on which to apply the change.

        """
        raise NotImplementedError

    @abstractmethod
    def revert(self, document):
        """ Revert the change represented by this modification.

        This is an abstract method which must be implemented by
        subclasses.

        Parameters
        ----------
        document : Document
            The document instance on which to revert the change.

        """
        raise NotImplementedError

    @abstractmethod
    def invalidated_span(self):
        """ Get the invalidated span for this modification.

        This is an abstract method which must be implemented by
        subclasses.

        Returns
        -------
        result : Span
            The span of the document region that was invalidated by this
            modification.

        """
        raise NotImplementedError


class InsertNewline(Modification):
    """ A document modification representing a newline insertion.

    """
    __slots__ = ('position',)

    def __init__(self, position):
        """ Initialize an InsertNewline.

        Parameters
        ----------
        position : Position
            The position of the newline insertion.

        """
        self.position = position

    def apply(self, document):
        """ Apply the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to apply the change.

        """
        document.insert_newline(self.position)

    def revert(self, document):
        """ Revert the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to revert the change.

        """
        document.remove_newline(self.position.lineno)

    def invalidated_span(self):
        """ Get the invalidated span for this modification.

        Returns
        -------
        result : Span
            The span of the document region that was invalidated by
            this modification.

        """
        return Span(self.position, Position(-1, -1))


class InsertInline(Modification):
    """ A document modification representing inline text insertion.

    """
    __slots__ = ('position', 'text')

    def __init__(self, position, text):
        """ Initialize an InsertInline.

        Parameters
        ----------
        position : Position
            The document position of the inserted text.

        text : unicode
            The text inserted inline into the document.

        """
        self.position = position
        self.text = text

    def apply(self, document):
        """ Apply the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to apply the change.

        """
        document.insert_inline(self.position, self.text)

    def revert(self, document):
        """ Revert the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to revert the change.

        """
        position = self.position
        start = position.column
        end = start + len(self.text)
        document.remove_inline(position.lineno, start, end)

    def invalidated_span(self):
        """ Get the invalidated span for this modification.

        Returns
        -------
        result : Span
            The span of the document region that was invalidated by
            this modification.

        """
        start = self.position
        return Span(start, Position(start.lineno, -1))


class InsertLines(Modification):
    """ A document modification representing multiple line insertion.

    """
    __slots__ = ('lineno', 'lines')

    def __init__(self, lineno, lines):
        """ Initialize an InsertLines.

        Parameters
        ----------
        lineno : int
            The line number of the insert.

        lines : list
            The list of unicode strings inserted in the document.

        """
        self.lineno = lineno
        self.lines = lines

    def apply(self, document):
        """ Apply the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to apply the change.

        """
        document.insert_lines(self.lineno, self.lines)

    def revert(self, document):
        """ Revert the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to revert the change.

        """
        start = self.lineno
        end = start + len(self.lines)
        document.remove_lines(start, end)

    def invalidated_span(self):
        """ Get the invalidated span for this modification.

        Returns
        -------
        result : Span
            The span of the document region that was invalidated by this
            modification.

        """
        return Span(Position(self.lineno, 0), Position(-1, -1))


class RemoveNewline(Modification):
    """ A document modification representing a newline removal.

    """
    __slots__ = ('position',)

    def __init__(self, position):
        """ Initialize a RemoveNewline.

        Parameters
        ----------
        position : Position
            The position of the newline removal.

        """
        self.position = position

    def apply(self, document):
        """ Apply the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to apply the change.

        """
        document.remove_newline(self.position.lineo)

    def revert(self, document):
        """ Revert the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to revert the change.

        """
        document.insert_newline(self.position)

    def invalidated_span(self):
        """ Get the invalidated span for this modification.

        Returns
        -------
        result : Span
            The span of the document region that was invalidated by
            this modification.

        """
        return Span(self.position, Position(-1, -1))


class RemoveInline(Modification):
    """ A document modification representing an inline removal.

    """
    __slots__ = ('position', 'text')

    def __init__(self, position, text):
        """ Initialize a RemoveInline.

        Parameters
        ----------
        position : Position
            The starting position of the removed text.

        text : unicode
            The text removed from the document.

        """
        self.position = position
        self.text = text

    def apply(self, document):
        """ Apply the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to apply the change.

        """
        position = self.position
        lineno = position.lineno
        start = position.column
        end = start + len(self.text)
        document.remove_inline(lineno, start, end)

    def revert(self, document):
        """ Revert the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to revert the change.

        """
        position = self.position
        document.insert_inline(position.lineno, position.column, self.text)

    def invalidated_span(self):
        """ Get the invalidated span for this modification.

        Returns
        -------
        result : Span
            The span of the document region that was invalidated by
            this modification.

        """
        start = self.position
        return Span(start, Position(start.lineno, -1))


class RemoveLines(Modification):
    """ A document modification representing multiple line removal.

    """
    __slots__ = ('lineno', 'lines')

    def __init__(self, lineno, lines):
        """ Initialize a RemoveLines.

        Parameters
        ----------
        lineno : int
            The line number of the removal.

        lines : list
            The list of unicode strings removed from the document.

        """
        self.lineno = lineno
        self.lines = lines

    def apply(self, document):
        """ Apply the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to apply the change.

        """
        start = self.lineno
        end = start + len(self.lines)
        document.remove_lines(start, end)

    def revert(self, document):
        """ Revert the change represented by this modification.

        Parameters
        ----------
        document : Document
            The document instance on which to revert the change.

        """
        document.insert_lines(self.lineno, self.lines)

    def invalidated_span(self):
        """ Get the invalidated span for this modification.

        Returns
        -------
        result : Span
            The span of the document region that was invalidated by
            this modification.

        """
        return Span(Position(self.lineno, 0), Position(-1, -1))

