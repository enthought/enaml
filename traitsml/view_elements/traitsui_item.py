from enthought.traits.api import HasTraits, Instance

from ..registry import register_element
from .element import Element


@register_element
class TraitsUIItem(Element):
    
    # The HasTraits object that will provide the traits ui view
    model = Instance(HasTraits)

    # The traits view for editing the object. Optional.
    view = Instance(HasTraits)

    # The handler for editing the object. Optional.
    handler = Instance(HasTraits)

    
