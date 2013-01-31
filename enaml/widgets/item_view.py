#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any, Bool

from enaml.core.declarative import Declarative, scope_lookup
from enaml.core.templated import Templated


class EditGroup(Templated):

    _is_setup = Bool(False)

    def setup(self):
        if not self._is_setup:
            with self.children_event_context():
                for identifiers, f_globals, descriptions in self._templates:
                    scope = identifiers.copy()
                    for descr in descriptions:
                        cls = scope_lookup(descr['type'], f_globals, descr)
                        instance = cls(self)
                        with instance.children_event_context():
                            instance.populate(descr, scope, f_globals)
            self._is_setup = True

    def teardown(self):
        if self._is_setup:
            with self.children_event_context():
                for child in self.children:
                    child.destroy()
            self._is_setup = False


class ItemView(Declarative):

    item = Any
