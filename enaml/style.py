from traits.api import (implements, Instance, HasStrictTraits, Property, 
                        TraitFactory, Str)


from .enaml_base import EnamlBase
from .util.decorators import protected
from .util.style_sheet import (StyleSheet, ReactiveStyleNode, StyleTrait,
                               IStyleNodeData)


@protected('node_data')
class BaseStyleNode(ReactiveStyleNode, EnamlBase):

    style_sheet = Instance(StyleSheet)

    node_data = Property

    cls = Str
    
    def _get_node_data(self):
        return StyleNodeData(style_node=self)


class StyleNodeData(HasStrictTraits):

    implements(IStyleNodeData)

    style_node = Instance(BaseStyleNode)

    def node_id(self):
        return self.style_node.parent._id

    def node_type(self):
        return self.style_node.parent._type
    
    def node_classes(self):
        return self.style_node.cls.strip()
    
    def parent_node(self):
        return self.style_node.parent.parent.style.node_data


def Style(style_trait='style_sheet', data_trait='node_data'):
    return StyleTrait(style_trait, data_trait).as_ctrait()

Style = TraitFactory(Style)


class StyleNode(BaseStyleNode):

    #---------------------------------------------------------------------------
    # Misc Styles
    #---------------------------------------------------------------------------
    color = Style

    text_align = Style

    text_decoration = Style

    #---------------------------------------------------------------------------
    # Layout Styles
    #---------------------------------------------------------------------------
    align = Style

    max_height = Style

    max_width = Style

    min_height = Style

    min_width = Style

    size_policy = Style

    spacing = Style

    stretch = Style

    #---------------------------------------------------------------------------
    # Background Styles
    #---------------------------------------------------------------------------
    # shorthand for specifying the background_color, background_image, 
    # background_repeat, and/or background_position styles
    background = Style

    background_color = Style

    background_image = Style

    background_repeat = Style

    background_position = Style

    background_attachment = Style

    background_clip = Style

    background_origin = Style

    #---------------------------------------------------------------------------
    # Border Styles
    #---------------------------------------------------------------------------
    # shorthand for specifying the border_color, border_style, 
    # and/or border_width styles
    border = Style

    # shorthand for specifying the border_top_color, border_top_style,
    # and/or border_top_width styles
    border_top = Style

    # shorthand for specifying the border_right_color, border_right_style,
    # and/or border_right_width styles
    border_right = Style

    # shorthand for specifying the border_bottom_color, border_bottom_style,
    # and/or border_bottom_width styles
    border_bottom = Style

    # shorthand for specifying the border_left_color, border_left_style,
    # and/or border_left_width styles
    border_left = Style

    # shorthand for setting the color on all borders.
    border_color = Style

    border_top_color = Style

    border_right_color = Style

    border_bottom_color = Style

    border_left_color = Style

    border_image = Style

    # shorthand for specifying all of the border's radii
    border_radius = Style

    border_top_left_radius = Style

    border_top_right_radius = Style

    border_bottom_right_radius = Style

    border_bottom_left_radius = Style

    # shorthand for specifying the style of all border edges
    border_style = Style

    border_top_style = Style

    border_right_style = Style

    border_bottom_style = Style

    border_left_style = Style

    # shorthand for specifying the (top, right, bottom, left) widths
    border_width = Style

    border_top_width = Style

    border_right_width = Style

    border_bottom_width = Style

    border_left_width = Style

    #---------------------------------------------------------------------------
    # Font Styles
    #---------------------------------------------------------------------------
    # shorthand for specifying font_family, font_size, font_style, 
    # and/or font_weight
    font = Style

    font_family = Style

    font_size = Style

    font_style = Style

    font_weight = Style

    #---------------------------------------------------------------------------
    # Margin Styles
    #---------------------------------------------------------------------------
    # shorthand for specifying margin_top, margin_right, margin_bottom
    # and/or margin_left
    margin = Style

    margin_top = Style

    margin_right = Style

    margin_bottom = Style

    margin_left = Style

    #---------------------------------------------------------------------------
    # Padding Styles
    #---------------------------------------------------------------------------
    # shorthand for specifying padding_top, padding_right, padding_bottom,
    # and/or padding_left
    padding = Style

    padding_top = Style

    padding_right = Style

    padding_bottom = Style

    padding_left = Style

