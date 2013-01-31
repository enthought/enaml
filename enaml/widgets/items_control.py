#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, List, Enum, Str, Callable

from enaml.widget.declarative import Declarative
from enaml.widgets.control import Control


class DisplayItem(Declarative):

    exclude = Bool(False)

    background = Str

    foreground = Str

    font = Str

    visible = Bool(True)


class DisplayGroup(Declarative):

    display_mode = Enum('implicit', 'explicit')

    background = Str

    foreground = Str

    font = Str

    visible = Bool(True)

    def display_items(self):
        for child in self.children:
            if isinstance(child, DisplayItem):
                yield child


class ItemsControl(Control):

    items = List

    view_finder = Callable

    def snapshot(self):
        snap = super(ItemsControl, Control).snapshot()
        return snap

    def bind(self):
        super(ItemsControl, self).bind()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _generate_items(self):
        groups = []
        targets = set()
        # Collect the items that should be displayed.
        for group in self.children:
            if isinstance(group, DisplayGroup):
                targets.add(group.name)
                items = []
                for item in group.children:
                    if isinstance(item, DisplayItem):
                        items.append(item)
                groups.append((child, items)


