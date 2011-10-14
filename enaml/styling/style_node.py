#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, BaseTuple

from .color import ColorTrait
from .font import FontTrait
from .layout import AlignmentTrait, MarginsTrait, SizeTrait, SizePolicyTrait, SpacingTrait, StretchTrait


class StyleClassTrait(BaseTuple):

    def validate(self, obj, name, value):
        if isinstance(value, basestring):
            res = tuple(val.strip() for val in value.split())
        elif isinstance(value, (list, tuple)):
            if all(isinstance(val, basestring) for val in value):
                res = tuple(val.strip() for val in value)
            else:
                res = ()
        else:
            res = ()
        return res


class StyleNode(HasTraits):

    #: The alignment of a widget in its parent layout
    alignment = AlignmentTrait

    #: The foreground color of a widget. This is usually text color.
    fgcolor = ColorTrait

    #: The background color of a widget.
    bgcolor = ColorTrait

    #: The font to use for the widget.
    font = FontTrait

    #: The margins to place around a layout.
    margins = MarginsTrait

    #: The suggested (w, h) size of the widget.
    size = SizeTrait

    #: How the widget should be resized when placed in a layout.
    size_policy = SizePolicyTrait

    #: The interelement spacing in a layout
    spacing = SpacingTrait

    #: The stretch factor to use when adding the widget to a layout
    stretch = StretchTrait

    #: The string name of the style class to use for this node.
    style_class = StyleClassTrait

