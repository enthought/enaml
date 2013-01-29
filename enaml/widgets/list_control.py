#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Enum, Range, Property, cached_property

from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size

from .control import Control
from .list_item import ListItem


class ListControl(Control):
    """ A `ListControl` displays a collection `ListItem` children.

    `ListItem` objects are flexible and convenient, but they are also
    fairly heavy weight. `ListControl` is well suited for use when the
    number of `ListItem` children is under ~1000.

    """
    #: The viewing mode of the list control. The 'list' mode arranges
    #: all items in a vertical list with small icons. The 'icon' mode
    #: uses large icons and a grid layout.
    view_mode = Enum('list', 'icon')

    #: Whether the items are fixed in place or adjusted during a resize.
    #: A relayout can be manually triggered at any time by calling the
    #: `refresh_item_layout()` method.
    resize_mode = Enum('adjust', 'fixed')

    #: The flow direction for the layout. A value of 'default' will
    #: allow the toolkit to choose an appropriate value based on the
    #: chosen view mode.
    flow_mode = Enum('default', 'top_to_bottom', 'left_to_right')

    #: Whether or not the layout items should wrap around at the widget
    #: boundaries. A value of None indicates the toolkit should choose
    #: proper value based on the view mode.
    item_wrap = Enum(None, True, False)

    #: Whether or not the text in the items should wrap at word
    #: boundaries when there is not enough horizontal space.
    word_wrap = Bool(False)

    #: The spacing to place between the items in the widget.
    item_spacing = Range(low=0, value=0)

    #: The size to render the icons in the list control. The default
    #: indicates that the toolkit is free to choose a proper size.
    icon_size = CoercingInstance(Size, (-1, -1))

    #: Whether or not the items in the model have uniform sizes. If
    #: all the items have uniform size, then the layout algorithm
    #: can be much more efficient on large models. If this is set
    #: to True, but the items do not have uniform sizes, then the
    #: behavior of the layout is undefined.
    uniform_item_sizes = Bool(False)

    #: The behavior used when laying out the items. In 'single_pass'
    #: mode, all items are laid out at once. In 'batch' mode, the
    #: items are laid out in batches of 'batch_size'. Batching can
    #: help make large models appear more interactive, but is not
    #: usually required for moderately sized models.
    layout_mode = Enum('single_pass', 'batched')

    #: The size of the layout batch when in 'batched' layout mode.
    batch_size = Range(low=0, value=100)

    #: A read only property which returns the control's list items.
    list_items = Property(depends_on='children')

    #: A list control expands freely in height and width by default.
    hug_width = 'weak'
    hug_height = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the list control.

        """
        snap = super(ListControl, self).snapshot()
        snap['view_mode'] = self.view_mode
        snap['resize_mode'] = self.resize_mode
        snap['flow_mode'] = self.flow_mode
        snap['item_wrap'] = self.item_wrap
        snap['word_wrap'] = self.word_wrap
        snap['item_spacing'] = self.item_spacing
        snap['icon_size'] = self.icon_size
        snap['uniform_item_sizes'] = self.uniform_item_sizes
        snap['layout_mode'] = self.layout_mode
        snap['batch_size'] = self.batch_size
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ListControl, self).bind()
        attrs = (
            'view_mode', 'resize_mode', 'flow_mode', 'item_wrap', 'word_wrap',
            'item_spacing', 'icon_size', 'uniform_item_sizes', 'layout_mode',
            'batch_size',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh_items_layout(self):
        """ Request an items layout refresh from the client widget.

        """
        self.send_action('refresh_items_layout', {})

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_list_items(self):
        """ The getter for the 'list_items' property.

        Returns
        -------
        result : tuple
            The tuple of ListItem children defined for this area.

        """
        isinst = isinstance
        items = (c for c in self.children if isinst(c, ListItem))
        return tuple(items)

