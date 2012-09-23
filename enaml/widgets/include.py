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
    into the list of children of its parent. Any objects assigned to the
    `objects` list of the Include will be parented by the parent of the
    Include. By default, an Include is not snappable and therefore acts
    like a shadow object, making it easier for the developer to manage 
    dynamic children.

    """
    #: The list of objects belong to this Include. The objects in this
    #: list will be automatically parented with the Include's parent.
    objects = List(Instance(Object))

    #: A boolean flag indicating whether to destroy the old objects that
    #: are removed from the parent. The default is True.
    destroy_old = Bool(True)

    #: By default, an Include does not support children.
    allow_children = False

    #: By default, an Include is not snappable. Since an Include simply
    #: manages the parenting of objects, there is no need for the client
    #: UI to know of its existence. This can be temporarily set to True
    #: when perform debug snapshots to get the full state of the tree.
    snappable = False

    def _ensure_parents(self):
        """ Update the parents for the current list of objects.

        This is a private method which is called internally as needed.

        """
        objects = self.objects
        parent = self.parent
        if parent is None:
            for obj in objects:
                obj.set_parent(None)
        else:
            idx = parent.children.index(self)
            parent.insert_children(idx + 1, objects)
        for obj in objects:
            obj.initialize()

    def _init_changed(self):
        """ Handle the `init` event for the include.

        This handler ensures that the current objects are parented.

        """
        self._ensure_parents()

    def _objects_changed(self, old, new):
        """ Handle the `objects` list changing in its entirety.

        This handler unparents the objects no longer in its control and
        the ensures the current objects are properly parented.

        """
        new_set = set(new)
        destroy = self.destroy_old
        for obj in old:
            if obj not in new_set:
                if destroy:
                    obj.destroy()
                else:
                    obj.set_parent(None)
        self._ensure_parents()

    def _objects_items_changed(self, evt):
        """ Handle the `objects` list changing in-place.

        This handler unparents the objects no longer in its control and
        the ensures the current objects are properly parented.

        """
        new_set = set(self.objects)
        destroy = self.destroy_old
        for obj in evt.removed:
            if obj not in new_set:
                if destroy:
                    obj.destroy()
                else:
                    obj.set_parent(None)
        self._ensure_parents()

