#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from .wx_factories import WX_FACTORIES


class WxBuilder(object):
    """ An object which manages building a WxObject tree from an Enaml
    snapshot dict.

    """
    def __init__(self, factories=None):
        """ Initialize a WxBuilder.

        Parameters
        ----------
        factories : dict or None
            A dictionary mapping an Enaml class name to function which
            will import and return the appropriate WxObject subclass.
            If None is provied, the default WX_FACTORIES dict will be
            used.

        """
        self._factories = factories or WX_FACTORIES

    def build(self, tree, parent, pipe):
        """ Build the Wx object tree for the given Enaml tree.

        Parameters
        ----------
        tree : dict
            An Enaml snapshot tree representing an object dict.

        parent : WxObject or None
            The parent for the tree, or None if the tree is top-level.

        pipe : wxActionPipe
            The action pipe to pass to new WxObject instances.

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
                    break
        if obj_cls is None:
            msg =  'Unhandled object type: %s:%s'
            item_class = tree['class']
            item_bases = tree['bases']
            logging.error(msg % (item_class, item_bases))
            return
        obj = obj_cls.construct(tree, parent, pipe, self)
        for child in tree['children']:
            self.build(child, obj, pipe)
        return obj

