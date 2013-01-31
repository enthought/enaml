#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any, Str, Int

from enaml.core.messenger import Messenger


class ItemEditor(Messenger):

    value = Any

    foreground = Str

    background = Str

    font = Str

    def snapshot(self):
        snap = super(ItemEditor, self).snapshot()
        snap['value'] = self.value
        return snap

    def bind(self):
        self.publish_attributes('value', 'foreground', 'background', 'font')


class StringEditor(ItemEditor):

    value = Str


class IntEditor(ItemEditor):

    value = Int
