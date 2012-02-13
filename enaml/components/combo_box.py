#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import List, Any, Callable, Int, Instance, Property, Str

from .control import Control, AbstractTkControl

from ..core.trait_types import EnamlEvent


class AbstractTkComboBox(AbstractTkControl):

    @abstractmethod
    def shell_labels_changed(self, value):
        raise NotImplementedError

    @abstractmethod
    def shell_index_changed(self, index):
        raise NotImplementedError


class ComboBox(Control):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items.
    To select multiple items from a collection of items use a ListBox.

    The combo box works by first using the to_string callable to convert
    the value and the list of items into strings for display and then 
    using the index of the combo box to make appropriate selections.

    .. note::
        - If a value is specified that does not exist in the list of
          items then the box is deselected and the index attribute will
          be set to -1. However, the value attribute will still be 
          assigned the invalid value.
        - If list of items is changed then component will try to find
          the current value in the list and select it. If the value is
          not found then the index will be updated to -1.
        - The selected event is only emitted when the user selects
          a valid value through the ui control, not when the value
          is changed programmatically.

    """
    #: The objects that compose the collection.
    items = List(Any)

    #: The currently selected item from the collection. If this value
    #: is set to a value that is not in :attr:`items` then the computed 
    #: :attr:`index` will be -1.
    value = Any

    #: The integer index of the current selection in items. If the index
    #: is out of range of :attr:`items` then the index it is set to -1, 
    #: and the current :attr:`value` is left unchanged.
    index = Property(Int, depends_on=['_value', 'items[]'])

    #: A callable which will convert the objects in the items list to
    #: strings for display. Defaults to str.
    to_string = Callable(str)

    #: A readonly property that holds the component items as a list of
    #: strings that are produced by the :attr:`to_string` attribute.
    labels = Property(List(Str), depends_on=['to_string', 'items[]'])

    #: A readonly property that will return the result of calling
    #: :attr:`to_string` on :attr:`value`
    selected_text = Property(Str, depends_on=['to_string', 'value'])

    #: Fired when a new selection is made by the user through the ui,
    #: but not when changed programatically. The event object will contain
    #: the selected value.
    selected = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. ComboBoxes hug 
    #: width weakly, by default.
    hug_width = 'weak'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkComboBox)

    #: An internal attribute that is used to synchronize :attr:`index`.
    _value = Any

    #--------------------------------------------------------------------------
    # Property Handlers
    #--------------------------------------------------------------------------
    def __value_default(self):
        """ The default value handler for :attr:`_value`.

        """
        return self.value

    def _get_index(self):
        """ The property getter for :attr:`index`.

        """
        try:
            idx = self.items.index(self._value)
        except ValueError:
            idx = -1
        return idx
            
    def _set_index(self, idx):
        """ The property setter for :attr:`index`. If the index is out 
        of bounds of :attr:`items`, then :attr:`index` is set to -1 and 
        :attr:`value` is left unchanged.

        """
        items = self.items
        if idx < 0 or idx > len(items):
           self._value = None
        else:
           self.value = items[idx]

    def _value_changed(self, val):
        """ Forwards a change in :attr:`value` to :attr:`_value` so 
        that :attr:`index` can be properly updated.

        """
        self._value = val

    def _get_labels(self):
        """ The property getter for :attr:`labels`. Converts the 
        component items to a list of string labels.

        """
        return map(self.to_string, self.items)
    
    def _get_selected_text(self):
        """ The property getter for :attr:`selected_text`.

        """
        return self.to_string(self.value)

