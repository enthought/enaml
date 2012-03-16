#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
""" Standard table model for using existing TabularAdapters from Traits
UI with the TableView.

"""

from collections import Sequence

from ..styling.brush import Brush
from ..styling.color import Color
from .abstract_item_model import (ALIGN_HCENTER, ALIGN_JUSTIFY, ALIGN_LEFT,
    ALIGN_RIGHT, ALIGN_VCENTER, AbstractTableModel, ITEM_IS_DRAG_ENABLED,
    ITEM_IS_DROP_ENABLED, ITEM_IS_EDITABLE, ITEM_IS_ENABLED, ITEM_IS_SELECTABLE)


class TabularAdapterModel(AbstractTableModel):
    """ Wrap a TabularAdapter from Traits UI for use with Enaml.

    """

    # Mapping for trait alignment values to Enaml alignment values.
    _alignment_map = {
        'left': ALIGN_LEFT,
        'right': ALIGN_RIGHT,
        'center': ALIGN_HCENTER,
        'justify': ALIGN_JUSTIFY,
    }

    def __init__(self, object, name, adapter, selectable=True, editable=False,
        draggable=False, auto_update=False):
        """ Initialize a TabularAdapterModel.

        """
        #: The object that holds the list.
        self.object = object
        #: The name of the List trait that we are adapting.
        self.name = name
        #: The TabularAdapter.
        self.adapter = adapter
        #: Whether the items are selectable or not.
        self.selectable = selectable
        #: Whether cells are editable or not.
        self.editable = editable
        #: Whether the user can move items by dragging.
        self.draggable = draggable
        #: Whether the cells should automatically update if they are viewing
        #: individual traits on HasTraits objects.
        self.auto_update = auto_update
        self._setup_listeners()

    #--------------------------------------------------------------------------
    # TabularAdapterModel Methods
    #--------------------------------------------------------------------------

    def item(self, index):
        """ Return the item from the edited object given the ModelIndex
        or row index int.

        """
        row = getattr(index, 'row', index)
        return self.adapter.get_item(self.object, self.name, row)

    #--------------------------------------------------------------------------
    # Structure Methods
    #--------------------------------------------------------------------------

    def column_count(self, parent=None):
        """ Count the number of columns in the children of an item.

        """
        return len(self.adapter.columns)

    def row_count(self, parent=None):
        """ Count the number of rows in the children of an item.

        """
        return self.adapter.len(self.object, self.name)

    #--------------------------------------------------------------------------
    # Data Methods
    #--------------------------------------------------------------------------

    def data(self, index):
        """ Returns the cell data from the data source converted to
        a string for display.

        """
        text = self.adapter.get_text(self.object, self.name, index.row,
            index.column)
        return text

    def tool_tip(self, index):
        """ Get the tool tip string for a given model index.

        """
        tooltip = self.adapter.get_text(self.object, self.name, index.row,
            index.column)
        if tooltip:
            return tooltip
        else:
            return None

    def font(self, index):
        """ Get the font for a given model index.

        """
        font = self.adapter.get_font(self.object, self.name, index.row,
            index.column)
        return font

    def alignment(self, index):
        """ Get the alignment of the text for a given model index.

        """
        align_string = self.adapter.get_alignment(self.object, self.name,
            index.column)
        alignment = self._alignment_map.get(align_string, ALIGN_LEFT)
        return ALIGN_VCENTER | alignment

    def background(self, index):
        """ The background brush to use for the given index.

        """
        tcolor = self.adapter.get_bg_color(self.object, self.name, index.row,
            index.column)
        return self._brush_from_traits_color(tcolor)

    def foreground(self, index):
        """ The foreground brush to use for the given index.

        """
        tcolor = self.adapter.get_text_color(self.object, self.name, index.row,
            index.column)
        return self._brush_from_traits_color(tcolor)

    def flags(self, index):
        """ Obtain the flags that specify user interaction with items.

        """
        flags = ITEM_IS_ENABLED
        if self.selectable:
            flags |= ITEM_IS_SELECTABLE

        if (self.editable and self.adapter.get_can_edit_cell(self.object,
            self.name, index.row, index.column) or
            self.adapter.get_can_edit(self.object, self.name, index.row)):
            flags |= ITEM_IS_EDITABLE

        if self.draggable and self.adapter.get_drag(self.object, self.name,
            index.row) is not None:
            flags |= ITEM_IS_DRAG_ENABLED | ITEM_IS_DROP_ENABLED

        return flags

    def set_data(self, index, value):
        """ Update a model item's data.

        """
        self.adapter.set_text(self.object, self.name, index.row, index.column, value)
        self.notify_data_changed(index, index)
        return True

    def horizontal_header_data(self, section):
        """ Get the horizontal label for a particular header section.

        """
        self.adapter.trait_set(
            object=self.object,
            name=self.name,
        )
        return self.adapter.get_label(section, self.object)

    def vertical_header_data(self, section):
        """ Get the vertical label for a particular header section.

        """
        self.adapter.trait_set(
            object=self.object,
            name=self.name,
        )
        return self.adapter.get_row_label(section, self.object)

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
                # Let from_rgba() raise an error if it has the wrong
                # number of arguments.
                ecolor = Color.from_rgba(*tcolor)
        brush = Brush(ecolor, None)
        return brush

    def _setup_listeners(self):
        """ Set up traits listeners on the edited object to update this
        model when necessary.

        """
        self.object.on_trait_change(self._reset_model, self.name+'_items',
            dispatch='ui')
        if self.auto_update:
            self.object.on_trait_change(self._refresh, self.name + '.-',
                dispatch='ui')
        self.adapter.on_trait_change(self._refresh, '+update', dispatch='ui')
        self.adapter.on_trait_change(self._reset_model, 'columns', dispatch='ui')

    def _remove_listeners(self):
        """ Remove all of the listeners.

        """
        self.object.on_trait_change(self._reset_model, self.name+'_items',
            remove=True)
        if self.auto_update:
            self.object.on_trait_change(self._refresh, self.name + '.-',
                remove=True)
        self.adapter.on_trait_change(self._refresh, '+update', remove=True)
        self.adapter.on_trait_change(self._reset_model, 'columns', remove=True)

    def _refresh(self):
        """ Refresh the visible data.

        """
        # FIXME: We should probably move this up to the view widget. It
        # can update its viewport. We just notify that everything has
        # changed.
        topleft = self.index(0, 0)
        bottomright = self.index(self.row_count()-1, self.column_count()-1)
        self.notify_data_changed(topleft, bottomright)

    def _reset_model(self):
        """ Reset the model.

        """
        self.begin_reset_model()
        self.end_reset_model()


