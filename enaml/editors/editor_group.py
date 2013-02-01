#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str

from enaml.core.declarative import scope_lookup
from enaml.core.templated import Templated

from .editor_items import EditorItem


class EditorGroup(Templated):
    """ A templated object which manages `EditorItem` children.

    An `EditorGroup` is used with a `ModelEditor` to manage a number of
    `EditorItem` children which belong in a conceptual edit group. The
    name of the group is specified with the `name` attribute.

    An `EditorGroup` will delay the creation of its children until they
    are explicitly requested. This allows an item-based view to be more
    efficient by only creating the editor items required for display.
    The children are created in an independent scope seeded with the
    scope of the editor group.

    """
    #: The background color of the editor group. Supports CSS3 color
    #: strings. An editor item will inherit this background unless
    #: it explicitly defines its own.
    background = Str

    #: The foreground color of the editor group. Supports CSS3 color
    #: strings. An editor item will inherit this foreground unless
    #: it explicitly defines its own.
    foreground = Str

    #: The font the editor group. Supports CSS3 shorthand font strings.
    #: An editor item will inherit this font unless it explicitly
    #: defines its own.
    font = Str

    #: A private flag indicating whether the children have been built.
    _built = Bool(False)

    def editor_items(self):
        """ Get the editor items defined on this group.

        This method will trigger the creation of the children the first
        time it is called.

        Returns
        -------
        result : generator
            A generator which will yield the group children which are
            instances of `EditorItem`.

        """
        self._build_if_needed()
        for child in self.children:
            if isinstance(child, EditorItem):
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

