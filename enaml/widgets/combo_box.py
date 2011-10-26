#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import List, Any, Event, Callable, Instance

from .control import Control, AbstractTkControl


class AbstractTkComboBox(AbstractTkControl):

    @abstractmethod
    def shell_items_changed(self, items):
        raise NotImplementedError

    @abstractmethod
    def shell_items_items_changed(self, items):
        raise NotImplementedError

    @abstractmethod
    def shell_value_changed(self, value):
        raise NotImplementedError
        
    @abstractmethod
    def shell_to_string_changed(self, to_string):
        raise NotImplementedError
    

class ComboBox(Control):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items. 
    To select multiple items from a collection of items use a ListBox.
    
    The combo box works by first using the to_string callable to convert 
    the value and the list of items into strings. If a value is specified 
    that does not exist in the list of items then the value is ignored 
    and the box is deselected.

    """
    #: The objects that compose the collection.
    items = List(Any)

    #: The currently selected item from the collection.
    value = Any

    #: A callable which will convert the objects in the items list to 
    #: strings for display. This callable should convert None to the
    #: empty string.
    to_string = Callable(str)

    #: Fired when a new selection is made. The args object will
    #: contain the selection.
    selected = Event

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkComboBox)
    
    # XXX we need to have the items handler here because the 
    # .add_trait_listener call does not add items event handlers
    # properly
    def _items_items_changed(self, items):
        self.abstract_obj.shell_items_items_changed(items)

