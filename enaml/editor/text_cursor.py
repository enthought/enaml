#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.signaling import Signal

from .abstract_text_document import AbstractTextDocument


class TextCursor(object):

    moved = Signal()

    def __init__(self, document):
        assert isinstance(document, AbstractTextDocument)
        self._doc = document
        self._lineno = 0
        self._pos = 0
        self._des = 0

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _update_location(self, lineno, pos, store_pos):
        if self._lineno != lineno or self._pos != pos:
            old = (self._lineno, self._pos)
            new = (lineno, pos)
            self._lineno = lineno
            self._pos = pos
            if store_pos:
                self._des = pos
            self.moved.emit(old, new)

    #--------------------------------------------------------------------------
    # Position
    #--------------------------------------------------------------------------
    def lineno(self):
        return self._lineno

    def position(self):
        return self._pos

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

