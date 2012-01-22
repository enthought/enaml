from collections import Sequence

from traits.api import Any, Instance
from traitsui.tabular_adapter import TabularAdapter

from ..styling.color import Color
from ..styling.brush import Brush
from .abstract_item_model import (
    AbstractTableModel, ITEM_IS_SELECTABLE,
    ITEM_IS_ENABLED, ITEM_IS_EDITABLE, ALIGN_LEFT, ALIGN_RIGHT, ALIGN_HCENTER,
    ALIGN_VCENTER, ALIGN_JUSTIFY
)

class TabularAdapterModel(AbstractTableModel):
    """ Wrap a TabularAdapter from Traits UI for use with Enaml.

    """

    #: The data object, typically a list of some kind.
    data_source = Any()

    #: The TabularAdapter.
    adapter = Instance(TabularAdapter)

    # Mapping for trait alignment values to Enaml alignment values.
    _alignment_map = {
        'left': ALIGN_LEFT,
        'right': ALIGN_RIGHT,
        'center': ALIGN_HCENTER,
        'justify': ALIGN_JUSTIFY,
    }

    def __init__(self, data_source, **kwargs):
        """ Initialize a TabularAdapterModel.

        Parameters
        ----------
        data_source : Any
            The data source object to use in this model

        **kwargs
            Any other attribute defaults.

        """
        # Set the data source quietly so we don't needlessly
        # trigger any traits listener updates
        self.trait_setq(data_source=data_source)
        super(TabularAdapterModel, self).__init__(**kwargs)

    def column_count(self, parent=None):
        """ Count the number of columns in the children of an item.

        """
        return len(self.adapter.columns)

    def row_count(self, parent=None):
        """ Count the number of rows in the children of an item.

        """
        return self.adapter.len(self, 'data_source')

    #--------------------------------------------------------------------------
    # Data Methods
    #--------------------------------------------------------------------------

    def data(self, index):
        """ Returns the cell data from the data source converted to
        a string for display.

        """
        text = self.adapter.get_text(self, 'data_source', index.row,
            index.column)
        return text

    def tool_tip(self, index):
        """ Get the tool tip string for a given model index.

        """
        tooltip = self.adapter.get_text(self, 'data_source', index.row,
            index.column)
        if tooltip:
            return tooltip
        else:
            return None

    def font(self, index):
        """ Get the font for a given model index.

        """
        font = self.adapter.get_font(self, 'data_source', index.row,
            index.column)
        return font

    def alignment(self, index):
        """ Get the alignment of the text for a given model index.

        """
        align_string = self.adapter.get_alignment(self, 'data_source',
            index.column)
        alignment = self._alignment_map.get(align_string, ALIGN_LEFT)
        return ALIGN_VCENTER | alignment

    def background(self, index):
        """ The background brush to use for the given index.

        """
        tcolor = self.adapter.get_bg_color(self, 'data_source', index.row,
            index.column)
        return self._brush_from_traits_color(tcolor)

    def foreground(self, index):
        """ The foreground brush to use for the given index.

        """
        tcolor = self.adapter.get_fg_color(self, 'data_source', index.row,
            index.column)
        return self._brush_from_traits_color(tcolor)

    def _brush_from_traits_color(self, tcolor):
        """ Return an Enaml Brush from a Traits color specification.

        """
        if tcolor is None:
            return None
        elif isinstance(tcolor, basestring):
            ecolor = Color.fromstring(tcolor)
        elif isinstance(tcolor, Sequence):
            if len(tcolor) == 3:
                ecolor = Color.from_rgb(*tcolor)
            else:
                # Let from_rgba() raise an error if it has the wrong number of
                # arguments.
                ecolor = Color.from_rgba(*tcolor)
        brush = Brush(ecolor, None)
        return brush

    def _data_source_changed(self):
        """ Notifies any attached views that our internal model has been
        reset and they should update their display.

        """
        self.begin_reset_model()
        self.end_reset_model()



