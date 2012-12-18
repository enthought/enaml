#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .cursor_interface import CursorInterface


class CaretTracker(object):
    def __init__(self, cursor):
        self.cursor = cursor
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        pass


class Caret(object):
    """ A lightweight object representing a caret in a TextListCursor.

    """
    def __init__(self, lineno=0, position=0, desired=0):
        self.lineno = lineno
        self.position = position
        self.desired = 0


class TextListCursor(CursorInterface):
    """ A concrete implementation of CursorInterface.

    This class is designed to be used with an instance of TextList. User
    code should not directly instatiate this class. Instead, an instance
    can be retrieved by calling the `cursor` method on a TextList object.

    """
    def __init__(self, text_list):
        """ Initialize a TextListCursor.

        Parameters
        ----------
        text_list : TextList
            The text list object which holds the text data.

        """
        self._text = text_list

        self._lineno = 0
        self._pos = 0
        self._des = 0

    #--------------------------------------------------------------------------
    # Cusor Interface
    #--------------------------------------------------------------------------
    def carets(self):
        return []

    #--------------------------------------------------------------------------
    # Movement
    #--------------------------------------------------------------------------
    def move_abs(self, lineno, pos):
        doc = self._doc
        lineno = max(0, min(lineno, doc.line_count() - 1))
        line = doc.line(lineno)
        pos = max(0, min(pos, len(line)))
        self._update_location(lineno, pos, True)

    def move_up(self, count=1):
        doc = self._doc
        lineno = max(0, self._lineno - count)
        pos = max(0, min(self._des, len(doc.line(lineno))))
        self._update_location(lineno, pos, False)

    def move_down(self, count=1):
        doc = self._doc
        lineno = min(self._lineno + count, doc.line_count() - 1)
        pos = max(0, min(self._des, len(doc.line(lineno))))
        self._update_location(lineno, pos, False)

    def move_left(self, count=1):
        pos = self._pos - count
        lineno = self._lineno
        if pos < 0:
            lineno -= 1
            doc = self._doc
            while pos < 0 and lineno >= 0:
                line = doc.line(lineno)
                pos += len(line) + 1
                lineno -= 1
            lineno += 1
            pos = max(0, pos)
        self._update_location(lineno, pos, True)

    def move_right(self, count=1):
        pos = self._pos + count
        lineno = self._lineno
        doc = self._doc
        line = doc.line(lineno)
        if pos > len(line):
            last_line = doc.line_count() - 1
            while True:
                if lineno == last_line:
                    pos = len(line)
                    break
                lineno += 1
                pos -= len(line) + 1
                line = doc.line(lineno)
                if pos <= len(line):
                    break
        self._update_location(lineno, pos, True)

    #--------------------------------------------------------------------------
    # Editing
    #--------------------------------------------------------------------------
    def insert(self, chars):
        self._doc.insert_chars(self._lineno, self._pos, chars)
        old = (self._lineno, self._pos)
        self._pos += len(chars)
        self._des = self._pos
        new = (self._lineno, self._pos)
        self.moved.emit(old, new)

    def backspace(self):
        pos = self._pos
        lineno = self._lineno
        doc = self._doc
        if pos > 0:
            rem_pos = pos - 1
            doc.remove_chars(lineno, rem_pos, rem_pos)
            self._pos = rem_pos
            self._des = self._pos
            self.moved.emit()
            return
        if lineno > 0:
            rem_line = doc.line(lineno)
            edit_lineno = lineno - 1
            ins_pos = len(doc.line(edit_lineno))
            doc.remove_line(lineno)
            doc.insert_chars(edit_lineno, ins_pos, rem_line)
            self._lineno = edit_lineno
            self._pos = ins_pos
            self._des = self._pos

    def delete(self):
        pos = self._pos
        lineno = self._lineno
        doc = self._doc
        line = doc.line(lineno)
        if pos < len(line):
            doc.remove_chars(lineno, pos, pos)
            return
        if doc.line_count() > lineno + 1:
            rem_line = doc[lineno + 1]
            doc.remove_line(lineno + 1)
            doc.insert_chars(lineno, pos, rem_line)

    def newline(self):
        pos = self._pos
        lineno = self._lineno
        doc = self._doc
        line = doc.line(lineno)
        edit_line = line[pos:]
        doc.remove_chars(lineno, pos, len(line) -1 )
        doc.insert_line(lineno + 1, edit_line)
        self._pos = 0
        self._lineno = lineno + 1

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

