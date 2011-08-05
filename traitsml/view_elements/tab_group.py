from enthought.traits.api import Bool, Enum, Int, Dict, Str

from ..constants import TabPosition
from ..registry import register_element
from .element import Element


@register_element
class TabGroup(Element):
    
    # The index of the currently shown tab.
    current_index = Int(-1)

    # Whether or not the tabs or movable in the group.
    movable = Bool
    
    # The list of names (in proper order) for the tabs.
    tab_names = Dict(Element, Str)

    # The position of the tab bar relative to the pages.
    tab_position = Enum(TabPosition.DEFAULT, *TabPosition.values())


