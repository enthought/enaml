#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements, HasStrictTraits, Str, WeakRef, cached_property

from .enaml_base import EnamlBase
from .style_sheet import IStyleNodeData, StyleNode


#-------------------------------------------------------------------------------
# Style Node definition
#-------------------------------------------------------------------------------
class EnamlStyleNode(EnamlBase, StyleNode):
    """ A StyleNode subclass for use with Enaml components.

    Attributes
    ----------
    parent : WeakRef
        A protected attribute which should hold a reference to the enaml
        component that created this node. The parent is used by the
        EnamlStyleNodeData object to get the required information to 
        query the style sheet.
    
    cls : Str
        A space separated string that is the style classes for this
        node.
    
    """
    parent = WeakRef

    cls = Str

    @cached_property
    def _get_node_data(self):
        """ Returns an implementor of IStyleNodeData for this node.

        """
        return EnamlStyleNodeData(style_node=self)

    def _style_trait_updated(self, obj, name, old, new):
        """ Handles style traits defined on this class changing.

        """
        self.refresh_tags((name,))

    def _cls_changed(self):
        """ Handles the class string changing by refreshing all tags.

        """
        self.refresh_tags(self.style_sheet.get_tags())

    def add_trait(self, name, trait):
        """ Overriden from the parent class to hookup listeners for
        changes to the traits and forward them as tag change events.

        """
        super(StyleNode, self).add_trait(name, trait)
        self.on_trait_change(self._style_trait_updated, name)


EnamlStyleNode.protect('parent', 'node_data', 'tag_updated')


class EnamlStyleNodeData(HasStrictTraits):
    """ A class that implements IStyleNodeData. Used by EnamlStyleNode.

    """
    implements(IStyleNodeData)

    style_node = WeakRef(EnamlStyleNode)

    def node_id(self):
        style_node = self.style_node
        if style_node is not None:
            return style_node.parent._id

    def node_type(self):
        style_node = self.style_node
        if style_node is not None:
            return style_node.parent._type
    
    def node_classes(self):
        style_node = self.style_node
        if style_node is not None:
            return style_node.cls.strip()
    
    def parent_node(self):
        style_node = self.style_node
        if style_node is not None:
            parent = style_node.parent.parent
            if parent is not None:
                return parent.style.node_data

