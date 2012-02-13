#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, List, Any, Int, Callable

from .control import Control, AbstractTkControl


# XXX check group needs to become a container subclass
class AbstractTkCheckGroup(AbstractTkControl):
    
    def parent_rows_changed(self, rows):
        """ Called when the number of rows changes. Will relayout the
        group according the to the number of rows.

        """
        raise NotImplementedError
    
    def parent_columns_changed(self, columns):
        """ Called when the number of columns changes. Will relayout the
        group according to the number of columns

        """
        raise NotImplementedError

    def parent_items_changed(self, items):
        """ Called when the list of items changes. Will relayout the 
        group according to the new items.

        """
        raise NotImplementedError

    def parent_selected_changed(self, selected_items):
        """ Called when the list of selected items changes. Will set
        the checked state of the appropriate check boxes.

        """
        raise NotImplementedError

    def parent_to_string_changed(self, to_string):
        """ Called when the to_string function changes. Will relabel
        the boxes according to the new coversion function.

        """
        raise NotImplementedError


class CheckGroup(Control):
    """ A control to select many from a set of items using check boxes.

    A CheckGroup presents a group of selectable items in the form of a
    group of check boxes. This is different from a RadioGroup where only
    one from a group of many may be selected.

    Attributes
    ----------
    rows : Int
        The number of rows to use for the group (more will be added 
        automatically if necessary.) Only values greater than zero are
        significant.
    
    columns : Int
        The number of columns to user for the group. Only values greater
        than zero are significant. Otherwise, the number is computed 
        automatically.
    
    items : List(Any)
        The list of items for which to create check boxes.

    selected : List(Any)
        The list of selected items (items with their boxes checked).
    
    to_string : Callable(str)
        The function to call to convert each item in the items list to 
        a string to use as the label for the check box. Defaults to str.
    
    """
    rows = Int

    columns = Int

    items = List(Any)

    selected = List(Any)

    to_string = Callable(str)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ICheckGroupImpl)

