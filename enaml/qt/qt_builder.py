#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from .qt_factories import QT_FACTORIES


class QtBuilder(object):
    """ An object which manages building Qt object tree from a Enaml
    snapshot dict.

    """
    def __init__(self, factories=None):
        """ Initialize a QtBuilder.

        Parameters
        ----------
        factories : dict or None
            A dictionary mapping an Enaml class name to function which
            will import and return the appropriate QtObject subclass.
            If None is provied, the default QT_FACTORIES dict will be
            used.

        """
        self._factories = factories or QT_FACTORIES

    def build(self, tree, parent, pipe):
        """ Build the Qt object tree for the given Enaml tree.

        Parameters
        ----------
        tree : dict
            An Enaml snapshot tree representing an object dict.

        parent : QtObject or None
            The parent for the tree, or None if the tree is top-level.

        pipe : QActionPipe
            The action pipe to pass to new QtObject instances.

        """
        factories = self._factories
        class_name = tree['class']
        if class_name in factories:
            obj_cls = factories[class_name]()
        else:
            obj_cls = None
            for base in tree['bases']:
                if base in factories:
                    obj_cls = factories[base]()
        if obj_cls is None:
            msg =  'Unhandled object type: %s:%s'
            item_class = tree['class']
            item_bases = tree['bases']
            logging.error(msg % (item_class, item_bases))
            return
        obj = obj_cls.construct(tree, parent, pipe)
        if parent is not None:
            parent.add_child(obj)
        for child in tree['children']:
            self.build(child, obj, pipe)
        return obj

