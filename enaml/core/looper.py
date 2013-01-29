#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import Iterable

from traits.api import Instance, Property, Tuple

from .declarative import scope_lookup
from .templated import Templated


class Looper(Templated):
    """ A templated object that repeats its templates over an iterable.

    The children of a `Looper` are used as a template when creating new
    objects for each item in the given `iterable`. Each iteration of the
    loop will be given an indenpendent scope which is the union of the
    outer scope and any identifiers created during the iteration. This
    scope will also contain `loop_index` and `loop_item` variables which
    are the index and value of the iterable, respectively.

    All items created by the looper will be added as children of the
    parent of the `Looper`. The `Looper` keeps ownership of all items
    it creates. When the iterable for the looper is changed, the old
    items will be destroyed.

    Creating a `Looper` without a parent is a programming error.

    """
    #: The iterable to use when creating the items for the looper.
    iterable = Instance(Iterable)

    #: A read-only property which returns the tuple of items created
    #: by the looper when it passes over the objects in the iterable.
    #: Each item in the tuple represents one iteration of the loop and
    #: is a tuple of the items generated during that iteration.
    items = Property(fget=lambda self: self._items, depends_on='_items')

    #: Private storage for the `items` property.
    _items = Tuple

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def post_initialize(self):
        """ A reimplemented initialization method.

        This method will create and initialize the loop items using the
        looper templates to generate the items.

        """
        self._refresh_loop_items()
        super(Looper, self).post_initialize()

    def pre_destroy(self):
        """ A pre destroy handler.

        The looper will destroy all of its items, provided that the
        items are not already destroyed and the parent is not in the
        process of being destroyed.

        """
        super(Looper, self).pre_destroy()
        if len(self._items) > 0:
            parent = self.parent
            if not parent.is_destroying:
                with parent.children_event_context():
                    for iteration in self._items:
                        for item in iteration:
                            if not item.is_destroyed:
                                item.destroy()

    def post_destroy(self):
        """ A post destroy handler.

        The looper will release all references to items after it has
        been destroyed.

        """
        super(Looper, self).post_destroy()
        self.iterable = None
        self._items = ()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _iterable_changed(self):
        """ A private change handler for the `iterable` attribute.

        If the iterable changes while the looper is active, the loop
        items will be refreshed.

        """
        if self.is_active:
            self._refresh_loop_items()

    def _refresh_loop_items(self):
        """ A private method which refreshes the loop items.

        This method destroys the old items and creates and initializes
        the new items.

        """
        items = []
        iterable = self.iterable
        templates = self._templates

        if iterable is not None and len(templates) > 0:
            for loop_index, loop_item in enumerate(iterable):
                # Each template is a 3-tuple of identifiers, globals, and
                # list of description dicts. There will only typically be
                # one template, but more can exist if the looper was
                # subclassed via enamldef to provided default children.
                iteration = []
                for identifiers, f_globals, descriptions in templates:
                    # Each iteration of the loop gets a new scope which
                    # is the union of the existing scope and the loop
                    # variables. This also allows the loop children to
                    # add their own independent identifiers. The loop
                    # items are constructed with no parent since they
                    # are parented via `insert_children` later on.
                    scope = identifiers.copy()
                    scope['loop_index'] = loop_index
                    scope['loop_item'] = loop_item
                    for descr in descriptions:
                        cls = scope_lookup(descr['type'], f_globals, descr)
                        instance = cls()
                        with instance.children_event_context():
                            instance.populate(descr, scope, f_globals)
                        iteration.append(instance)
                items.append(tuple(iteration))

        old_items = self._items
        self._items = items = tuple(items)
        if len(old_items) > 0 or len(items) > 0:
            with self.parent.children_event_context():
                if len(old_items) > 0:
                    for iteration in old_items:
                        for old in iteration:
                            if not old.is_destroyed:
                                old.destroy()
                if len(items) > 0:
                    flat = sum(items, ())
                    self.parent.insert_children(self, flat)
                    for item in flat:
                        item.initialize()

