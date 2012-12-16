#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import codecs

import blist

from .abstract_text_document import AbstractTextDocument


class TextDocument(AbstractTextDocument):

    @classmethod
    def from_string(cls, string):
        lines = blist.blist()
        for line in string.splitlines():
            lines.append(unicode(line))
        self = cls()
        self._lines = lines
        return self

    @classmethod
    def from_file(cls, filename):
        lines = blist.blist()
        with codecs.open(filename, encoding='utf-8') as f:
            for line in f:
                lines.append(line.rstrip())
        self = cls()
        self._lines = lines
        return self

    @classmethod
    def from_iter(cls, iterable):
        lines = blist.blist()
        for line in iterable:
            lines.append(unicode(line.strip()))
        self = cls()
        self._lines = lines
        return self

    def __init__(self):
        self._lines = blist.blist([u''])

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def __iter__(self):
        return iter(self._lines)

    def line(self, lineno):
        return self._lines[lineno]

    def line_count(self):
        return len(self._lines)

    def to_string(self, ending=u'\n'):
        return ending.join(self._lines)

    def insert_chars(self, lineno, pos, chars):
        lines = self._lines
        line = lines[lineno]
        edit_line = line[:pos] + chars + line[pos:]
        lines[lineno] = edit_line
        self.chars_inserted.emit(lineno, pos, chars)

    def replace_chars(self, lineno, start, end, chars):
        lines = self._lines
        line = lines[lineno]
        rem_chars = line[start:end + 1]
        edit_line = line[:start] + chars + line[end + 1:]
        lines[lineno] = edit_line
        self.chars_replaced.emit(lineno, start, end, rem_chars, chars)

    def remove_chars(self, lineno, start, end):
        lines = self._lines
        line = lines[lineno]
        rem_chars = line[start:end + 1]
        edit_line = line[:start] + line[end + 1:]
        lines[lineno] = edit_line
        self.chars_removed.emit(lineno, start, end, rem_chars)

    def insert_line(self, lineno, line):
        lines = self._lines
        old_count = len(lines)
        lines.insert(lineno, line)
        self.line_inserted.emit(lineno, line)
        self.line_count_changed.emit(lineno, old_count, old_count + 1)

    def replace_line(self, lineno, line):
        lines = self._lines
        rem_line = lines[lineno]
        lines[lineno] = line
        self.line_replaced.emit(lineno, rem_line, line)

    def remove_line(self, lineno):
        lines = self._lines
        old_count = len(lines)
        rem_line = lines[lineno]
        del lines[lineno]
        self.line_removed.emit(lineno, rem_line)
        self.line_count_changed.emit(old_count, old_count - 1)

    def insert_block(self, lineno, block):
        lines = self._lines
        old_count = len(lines)
        for line in reversed(block):
            lines.insert(lineno, line)
        new_count = len(lines)
        self.block_inserted.emit(lineno, block)
        self.line_count_changed.emit(old_count, new_count)

    def replace_block(self, start, end, block):
        lines = self._lines
        old_count = len(lines)
        old_block = list(lines[start:end + 1])
        del lines[start:end + 1]
        block = list(block)
        for line in reversed(block):
            lines.insert(start, line)
        new_count = len(lines)
        self.block_replaced.emit(start, end, old_block, block)
        self.line_count_changed.emit(old_count, new_count)

    def remove_block(self, start, end):
        lines = self._lines
        old_count = len(lines)
        old_block = list(lines[start:end + 1])
        del lines[start:end + 1]
        new_count = len(lines)
        self.block_removed.emit(start, end, old_block)
        self.line_count_changed.emit(old_count, new_count)

