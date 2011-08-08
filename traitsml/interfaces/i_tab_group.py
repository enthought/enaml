from traits.api import Bool, Enum, Int, Dict, Str

from ..constants import TabPosition
from .i_element import IElement


class ITabGroup(IElement):
    
    # The index of the currently shown tab.
    current_index = Int(-1)

    # Whether or not the tabs or movable in the group.
    movable = Bool
    
    # The list of names (in proper order) for the tabs.
    tab_names = Dict(IElement, Str)

    # The position of the tab bar relative to the pages.
    tab_position = Enum(TabPosition.DEFAULT, *TabPosition.values())


