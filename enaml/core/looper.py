#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import Iterable

from traits.api import Instance, Property, ReadOnly, Tuple

from .declarative import Declarative


#: A global readonly trait instance that is reused for all loop items.
_RO_TRAIT = ReadOnly()


class Looper(Declarative):
    """ A declarative object that repeats its children over an iterable.

    The children of a `Looper` are used as a template when creating new
    objects for each item in the given `iterable`. The objects created
    for each item in the `iterable` will be given a `loop_index` and a
    `loop_item` attribute which will contain the index and the item in
    the iterable, respectively.

    All items created by the looper will be added as children of the
    parent of the `Looper`. The `Looper` keeps ownership of all items
    it creates. When the iterable for the looper is changed, the old
    items will be destroyed.

    """
    #: The iterable to use when creating the items for the looper.
    iterable = Instance(Iterable)

    #: A read-only property which returns the tuple of items created
    #: by the looper when it passes over the objects in the iterable.
    items = Property(fget=lambda self: self._items, depends_on='_items')

    #: Private internal storage for the `items` property.
    _items = Tuple

    def initialize(self):
        """ A reimplemented initialization method.

        This method will create and initialize the loop items using the
        children of the looper as a template for creating the new items.
        The looper's children are not initialized.

        """
        self.state = 'initializing'
        self.pre_initialize()
        self._refresh_loop_items()
        self.state = 'initialized'
        self.post_initialize()

    def activate(self, session):
        """ A reimplemented activation method.

        This method does not activate the children of the looper, since
        they only serve as templates for the creation of the loop items.

        """
        self.state = 'activating'
        self.pre_activate(session)
        self._session = session
        session.register(self)
        self.state = 'active'
        self.post_activate(session)

    def post_destroy(self):
        """ A post destroy handler.

        The looper will drop all references to the created items when
        it is destroyed.

        """
        super(Looper, self).post_destroy()
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
        template = self.children
        ro_trait = _RO_TRAIT

        # The inner loop adds two read only traits to each new item so
        # that the items can access the `loop_index` and `loop_item`.
        # The traits are addded manually instead of using `add_trait`,
        # which avoids a bunch of unneeded and expensive checks. The
        # same read only trait can be reused with all instances, which
        # helps to save memory when a large number of items are created.
        if iterable is not None and len(template) > 0:
            for loop_index, loop_item in enumerate(iterable):
                for target in template:
                    item = type(target)()
                    items.append(item)
                    idict = item.__dict__
                    idict['loop_index'] = loop_index
                    idict['loop_item'] = loop_item
                    itraits = item._instance_traits()
                    itraits['loop_index'] = ro_trait
                    itraits['loop_item'] = ro_trait
                    if isinstance(target, Declarative):
                        expressions = target.bound_expressions()
                        listeners = target.bound_listeners()
                        for key, value in expressions.iteritems():
                            item.bind_expression(key, value)
                        for key, values in listeners.iteritems():
                            for listener in values:
                                item.bind_listener(key, listener)

        old_items = self._items
        self._items = items = tuple(items)
        if len(old_items) > 0 or len(items) > 0:
            with self.parent.children_event_context():
                if len(old_items) > 0:
                    for old in old_items:
                        old.destroy()
                if len(items) > 0:
                    self.parent.insert_children(self, items)
                    for item in items:
                        item.initialize()

