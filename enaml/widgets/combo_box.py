#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (List, Any, Event, Callable, Int,
                        Instance, Property, Undefined, Str)

from .control import Control, AbstractTkControl


class AbstractTkComboBox(AbstractTkControl):

    @abstractmethod
    def shell_items_changed(self, items):
        raise NotImplementedError

    @abstractmethod
    def shell_items_items_changed(self, items):
        raise NotImplementedError

    @abstractmethod
    def shell__index_changed(self, value):
        raise NotImplementedError

    @abstractmethod
    def shell_to_string_changed(self, to_string):
        raise NotImplementedError


class ComboBox(Control):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items.
    To select multiple items from a collection of items use a ListBox.

    The combo box works by first using the to_string callable to convert
    the value and the list of items into strings.

    .. note::
        - If a value is specified that does not exist in the list of
          items then the assigment is ignored and the box is deselected.
          In that case the component value will be Undefined.
        - If list of items is changed then component should try to find
          the current value in the list and select it. If the value is
          not found the value will change to Undefined. This behaviour
          needs to be implemented in the toolkit side.


    """
    #: The objects that compose the collection.
    items = List(Any)

    #: The currently selected item from the collection. Default value is
    #: Undefined. The attribute is implemented as a property over the
    #: internal :attr:`_index` attribute
    value = Property(Any, depends_on = '_index')

    #: A callable which will convert the objects in the items list to
    #: strings for display. This callable should convert None to the
    #: empty string.
    to_string = Callable(str)

    #: Fired when a new selection is made py the user or programmaticaly.
    #: The args object will contain the selection.
    selected = Event

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkComboBox)

    def _items_items_changed(self, new):
        """ Despatch the change event in the items of the list to
        the toolkits implementation.

        We need to have the items handler here because the
        .add_trait_listener call does not add items event handlers
         properly

        """
        self.abstract_obj.shell_items_items_changed(new)

    #--------------------------------------------------------------------------
    # Private properies
    #--------------------------------------------------------------------------

    #: Readonly property that holds the component items as a list of
    #: labels that are produced by the :attr:`to_string` attribute.
    _labels = Property(List(Any))

    #: Readonly property that holds the string representation of the
    #: current selection.
    _selection = Property(Str)

    #: Internal property that holds the index of the current selection.
    #: if no item is selected then :attr:`_index` is -1.
    _index = Int(-1)

    def _get__labels(self):
        """ Convert the component items to a list of labels.

        """
        # FIXME: this might raise an error
        return map(self.to_string, self.items)

    def _get__selection(self):
        """ Convert the current selected value into it's string
        representation.
        """
        # FIXME: this might raise an error
        if self.value is Undefined:
            return ''
        else:
            return self.to_string(self.value)

    def _get_value(self):
        """ Getter function for the ComboBox value.

        If :attr:`_index` is -1 then returns Undefined else it returns
        the currently selected value.

        """
        index = self._index
        if index == -1:
            return Undefined
        else:
            return self.items[index]

    def _set_value(self, value):
        """ Setter function for the ComboBox value.

        The method checks if ``value`` exists in :attr:`items` and assigns
        the appropriate value to :attr:`_index`. If value is not present
        then :attr:`_index` is set to -1.

       """
        items = self.items
        if value in items:
            index = items.index(value)
        else:
            index = -1
        self._index = index
