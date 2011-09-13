from traits.api import (implements, Instance, HasStrictTraits, Str, Property,
                        on_trait_change, WeakRef, Event)

from ..enaml_base import EnamlBase
from ..util.style_sheet import IStyleNodeData, StyleSheet


#-------------------------------------------------------------------------------
# Style names
#-------------------------------------------------------------------------------
STYLE_NAMES = set([
    "color",
    "text_align",
    "text_decoration",
    "align",
    "max_height",
    "max_width",
    "min_height",
    "min_width",
    "size_policy",
    "spacing",
    "stretch",
    "background_color",
    "background_image",
    "background_repeat",
    "background_position",
    "background_attachment",
    "background_clip",
    "background_origin",
    "border_color",
    "border_top_color",
    "border_right_color",
    "border_bottom_color",
    "border_left_color",
    "border_width",
    "border_top_width",
    "border_right_width",
    "border_bottom_width",
    "border_left_width",
])


#-------------------------------------------------------------------------------
# Style Node definition
#-------------------------------------------------------------------------------
class StyleNode(EnamlBase):

    _parent = WeakRef

    node_data = Property

    tag_updated = Event

    style_sheet = Instance(StyleSheet)

    cls = Str

    def _get_node_data(self):
        return StyleNodeData(style_node=self)

    def _style_trait_updated(self, obj, name, old, new):
        self.tag_updated = name

    @on_trait_change('style_sheet:updated')
    def _style_sheet_updated(self, updated):
        for tag in updated:
            self.tag_updated = tag

    @on_trait_change('style_sheet')
    def _style_sheet_swapped(self):
        for tag in STYLE_NAMES:
            self.tag_updated = tag
    
    @on_trait_change('cls')
    def _style_cls_updated(self):
        for tag in STYLE_NAMES:
            self.tag_updated = tag

    def add_trait(self, name, trait):
        """ Overriden from the parent class to add metadata to the added
        trait to help users of this class hook up listeners.

        """
        super(StyleNode, self).add_trait(name, trait)
        if name in STYLE_NAMES:
            self.on_trait_change(self._style_trait_updated, name)

    def get_tag(self, tag):
        try:
            res = getattr(self, tag)
        except AttributeError:
            res = self.style_sheet.get_property(tag, self.node_data)
        return res


StyleNode.protect('_parent', 'node_data', 'tag_updated')


class StyleNodeData(HasStrictTraits):

    implements(IStyleNodeData)

    style_node = Instance(StyleNode)

    def node_id(self):
        return self.style_node._parent._id

    def node_type(self):
        return self.style_node._parent._type
    
    def node_classes(self):
        return self.style_node.cls.strip()
    
    def parent_node(self):
        return self.style_node._parent.parent.style._node_data


class StyleHandler(HasStrictTraits):

    style_node = Instance(StyleNode)

    style_dict = Instance(dict, ())

    @on_trait_change('style_node:tag_updated')
    def _tag_updated(self, tag):
        self._update_tag(tag)

    def _update_tag(self, tag, null=object(), no_op=lambda *a, **k: None):
        style_dict = self.style_dict
        old = style_dict.get(tag, null)
        new = self.style_node.get_tag(tag)
        if old != new:
            style_dict[tag] = new
            name = 'style_%s' % tag
            getattr(self, name, no_op)(new)

