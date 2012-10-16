#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance, Bool

from enaml.core.declarative import Declarative
from enaml.core.object import Object


class Include(Declarative):
    """ An object which dynamically inserts children into its parent.

    The Include object can be used to cleanly and easily insert objects
    into the children of its parent. Object assigned to the `objects`
    list of the Include will be parented by the parent of the Include.
    By default, an Include is not snappable and therefore acts like a
    shadow object with no client widget representation.

    """
    #: The list of objects belonging to this Include. Objects in this
    #: list will be automatically parented with the Include's parent.
    objects = List(Instance(Object))

    #: A boolean flag indicating whether to destroy the old objects that
    #: are removed from the parent. The default is True.
    destroy_old = Bool(True)

    #: By default, an Include is not snappable. Since an Include simply
    #: manages the parenting of objects, there is no need for the client
    #: UI to know of its existence. This can be temporarily set to True
    #: when performing debug snapshots to get the full state of the tree.
    #: XXX provide a snaphshot method!
    snappable = False

    def _init_changed(self):
        """ A change handler for the `init` event of the Include.

        This handler ensures that the current objects are parented and
        properly initialized during the initialization pass.

        """
        parent = self.parent
        if parent is not None:
            objects = self.objects
            parent.insert_children(self, objects)
            # During an initialization pass, the parent is not yet fully
            # initialized and will therefore not initialize any children
            # which are being added. It is the repsonsibility of the
            # Include to initially initialize the objects.
            for child in objects:
                child.initialize()

    def _parent_changed(self, parent):
        """ A change handler for the `parent` of the Include.

        This handler will reparent the list of objects provided that
        the Include is fully initialized.

        """
        if self.initialized:
            objects = self.objects
            if parent is None:
                for child in objects:
                    child.set_parent(None)
            else:
                parent.insert_children(self, objects)

    def _objects_changed(self, old, new):
        """ A change handler for the `objects` list of the Include.

        This handler will replace the old children with the new children
        in a single atomic operation.

        """
        parent = self.parent
        if parent is not None:
            parent.replace_children(old, self, new, self.destroy_old)

    def _objects_items_changed(self, event):
        """ Handle the `objects` list changing in-place.

        This handler will replace the old children with the new children
        in a single atomic operation.

        """
        parent = self.parent
        if parent is not None:
            old = event.removed
            parent.replace_children(old, self, self.objects, self.destroy_old)

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def validate_children(self, children):
        """ A children validator which rejects all children.

        """
        if children:
            name = type(self).__name__
            msg = 'Cannot add children to component of type `%s`'
            raise ValueError(msg % name)
        return children

