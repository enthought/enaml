#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (HasStrictTraits, DelegatesTo, WeakRef, Bool,
                        on_trait_change, implements)

from .style_sheet import IStyleNodeData, NO_STYLE


class StyleManager(HasStrictTraits):

    implements(IStyleNodeData)

    component = WeakRef('enaml.widgets.component.Component')

    style_sheet = DelegatesTo('parent')

    style_node = DelegatesTo('parent')

    listen = Bool(False)

    @on_trait_change('style_sheet')
    def sheet_changed(self, sheet):
        if self.listen:
            self.apply()

    @on_trait_change('style_sheet:updated')
    def sheet_updated(self, tags):
        if self.listen:
            self.update_tags(tags)

    def apply(self, set_listen=True):
        style_sheet = self.style_sheet
        tags = set(style_sheet.get_tags())
        self.update_tags(tags)
        if set_listen:
            self.listen = True
    
    def update_tags(self, tags):
        style_sheet = self.style_sheet
        style_node = self.style_node
        for tag in tags:
            if hasattr(style_node, tag):
                val = style_sheet.get_property(tag, self)
                if val is not NO_STYLE:
                    setattr(style_node, tag, val)

    #--------------------------------------------------------------------------
    # IStyleNodeData interface
    #--------------------------------------------------------------------------
    def node_id(self):
        """ Returns the id of the element being styled as a string.

        """
        return self.component.identifier
    
    def node_classes(self):
        """ Returns the classes of the element being styled as a space
        separated string.

        """
        return self.style_node.style_class
    
    def node_type(self):
        """ Returns the type of the element being styled as a string.

        """
        return self.component.type_name

    def parent_node(self):
        """ Returns an IStyleNodeData object for the parent element of the
        element being styled.

        """
        return self.component.parent.style_manager

