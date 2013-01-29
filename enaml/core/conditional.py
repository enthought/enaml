#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Tuple, Property

from .declarative import scope_lookup
from .templated import Templated


class Conditional(Templated):
    """ A templated object that represents conditional objects.

    When the `condition` attribute is True, the conditional will create
    its template items and insert them into its parent; when False, the
    old items will be destroyed.

    Creating a `Conditional` without a parent is a programming error.

    """
    #: The condition variable. If this is True, a copy of the children
    #: will be inserted into the parent. Otherwise, the old copies will
    #: be destroyed.
    condition = Bool(True)

    #: A read-only property which returns the tuple of items created
    #: by the conditional when `condition` is True.
    items = Property(fget=lambda self: self._items, depends_on='_items')

    #: Private internal storage for the `items` property.
    _items = Tuple

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def post_initialize(self):
        """ A reimplemented initialization method.

        This method will create and initialize the conditional items
        using the children of the conditional as a template.

        """
        self._refresh_conditional_items()
        super(Conditional, self).post_initialize()

    def pre_destroy(self):
        """ A pre destroy handler.

        The conditional will destroy all of its items, provided that
        the items are not already destroyed and the parent is not in
        the process of being destroyed.

        """
        super(Conditional, self).pre_destroy()
        if len(self._items) > 0:
            parent = self.parent
            if not parent.is_destroying:
                with parent.children_event_context():
                    for item in self._items:
                        if not item.is_destroyed:
                            item.destroy()

    def post_destroy(self):
        """ A post destroy handler.

        The conditional will release all references to items after it
        has been destroyed.

        """
        super(Conditional, self).post_destroy()
        self._items = ()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _condition_changed(self, condition):
        """ A private change handler for the `condition` attribute.

        If the iterable changes while the looper is active, the items
        will be refreshed.

        """
        if self.is_active:
            self._refresh_conditional_items()

    def _refresh_conditional_items(self):
        """ A private method which refreshes the conditional items.

        This method destroys the old items and creates and initializes
        the new items.

        """
        items = []
        condition = self.condition
        templates = self._templates

        if condition and len(templates) > 0:
            # Each template is a 3-tuple of identifiers, globals, and
            # list of description dicts. There will only typically be
            # one template, but more can exist if the conditional was
            # subclassed via enamldef to provided default children.
            for identifiers, f_globals, descriptions in templates:
                # Each conditional gets a new scope derived from the
                # existing scope. This also allows the new children
                # to add their own independent identifiers. The items
                # are constructed with no parent since they are
                # parented via `insert_children` later on.
                scope = identifiers.copy()
                for descr in descriptions:
                    cls = scope_lookup(descr['type'], f_globals, descr)
                    instance = cls()
                    with instance.children_event_context():
                        instance.populate(descr, scope, f_globals)
                    items.append(instance)

        old_items = self._items
        self._items = items = tuple(items)
        if len(old_items) > 0 or len(items) > 0:
            with self.parent.children_event_context():
                if len(old_items) > 0:
                    for old in old_items:
                        if not old.is_destroyed:
                            old.destroy()
                if len(items) > 0:
                    self.parent.insert_children(self, items)
                    for item in items:
                        item.initialize()

