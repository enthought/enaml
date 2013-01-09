#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple


class Position(namedtuple('PositionBase', 'lineno column')):
    """ A namedtuple representing a position in a Document.

    Parameters
    ----------
    lineno : int
        The line number of the position in the document. This must
        be greater than or equal to zero. However, a value of -1
        is allowed and represents the last line of the document.

    column : int
        The column of the position in the document. This must be
        greater than or equal to zero. However, a value of -1 is
        allowed and represents the last column of the line.

    """
    __slots__ = ()


class Span(namedtuple('SpanBase', 'start end')):
    """ A namedtuple representing a range of text in a Document.

    Parameters
    ----------
    start : Position
        The starting position of the span.

    end : Position
        The ending position of the span.

    """
    __slots__ = ()

