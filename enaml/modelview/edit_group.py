#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str

from enaml.core.declarative import scope_lookup
from enaml.core.templated import Templated

from .item import Item


class EditGroup(Templated):
    """ A templated object which manages `Item` children.

    An `EditGroup` is used with a `ModelEditor` to manage a number of
    `Item` children which belong to a conceptual group. The name of the
    group is specified with the `name` attribute.

    An `EditGroup` will delay the creation of its children until they
    are explicitly requested. This allows the underlying item model to
    be more efficient by only creating the items required for display.

    Children are created in an independent scope seeded with the scope
    of the editor group. Children created by one group will not have
    access to those created by another group.

    """
    #: The background color of the editor group. Supports CSS3 color
    #: strings.
    background = Str

    #: The foreground color of the editor group. Supports CSS3 color
    #: strings.
    foreground = Str

    #: The font the editor group. Supports CSS3 shorthand font strings.
    font = Str

    #: A private flag indicating whether the children have been built.
    _built = Bool(False)

    def items(self):
        """ Get the items defined on this edit group.

        Returns
        -------
        result : generator
            A generator which will yield the group children which are
            instances of `Item`.

        """
        self._build_if_needed()
        for child in self.children:
            if isinstance(child, Item):
                yield child

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _build_if_needed(self):
        """ Create and initialize the children if needed.

        This method will create and intialize the children of the group
        the first time it is called. Afterwards, it is no-op unless the
        private `_built` flag is reset to False.

        """
        if self._built:
            return
        self._built = True
        with self.children_event_context():
            for identifiers, f_globals, descriptions in self._templates:
                scope = identifiers.copy()
                for descr in descriptions:
                    cls = scope_lookup(descr['type'], f_globals, descr)
                    instance = cls(self)
                    with instance.children_event_context():
                        instance.populate(descr, scope, f_globals)
                    instance.initialize()

