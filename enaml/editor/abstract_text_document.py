#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from enaml.signaling import Signal


class AbstractTextDocument(object):

    __metaclass__ = ABCMeta

    chars_inserted = Signal()

    chars_replaced = Signal()

    chars_removed = Signal()

    line_inserted = Signal()

    line_replaced = Signal()

    line_removed = Signal()

    block_inserted = Signal()

    block_replaced = Signal()

    block_removed = Signal()

    line_count_changed = Signal()

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abstractmethod
    def line(self, lineno):
        raise NotImplementedError

    @abstractmethod
    def line_count(self):
        raise NotImplementedError

    @abstractmethod
    def to_string(self):
        raise NotImplementedError

    @abstractmethod
    def insert_chars(self, lineno, pos, chars):
        raise NotImplementedError

    @abstractmethod
    def replace_chars(self, lineno, start, end, chars):
        raise NotImplementedError

    @abstractmethod
    def remove_chars(self, lineno, start, end):
        raise NotImplementedError

    @abstractmethod
    def insert_line(self, lineno, line):
        raise NotImplementedError

    @abstractmethod
    def replace_line(self, lineno, line):
        raise NotImplementedError

    @abstractmethod
    def remove_line(self, lineno):
        raise NotImplementedError

    @abstractmethod
    def insert_block(self, lineno, block):
        raise NotImplementedError

    @abstractmethod
    def replace_block(self, start, end, block):
        raise NotImplementedError

    @abstractmethod
    def remove_block(self, start, end):
        raise NotImplementedError

